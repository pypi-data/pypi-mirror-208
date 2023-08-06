import psutil
from enum import Enum
from cli_args import args
import threading
from loguru import logger
from contextlib import nullcontext

class VRAMState(Enum):
    CPU = 0
    NO_VRAM = 1
    LOW_VRAM = 2
    NORMAL_VRAM = 3
    HIGH_VRAM = 4
    MPS = 5

# Determine VRAM State
vram_state = VRAMState.NORMAL_VRAM
set_vram_to = VRAMState.NORMAL_VRAM

total_vram = 0
total_vram_available_mb = -1

accelerate_enabled = False
xpu_available = False

try:
    import torch
    try:
        import intel_extension_for_pytorch as ipex
        if torch.xpu.is_available():
            xpu_available = True
            total_vram = torch.xpu.get_device_properties(torch.xpu.current_device()).total_memory / (1024 * 1024)
    except:
        total_vram = torch.cuda.mem_get_info(torch.cuda.current_device())[1] / (1024 * 1024)
    total_ram = psutil.virtual_memory().total / (1024 * 1024)
    if not args.normalvram and not args.cpu:
        if total_vram <= 4096:
            print("Trying to enable lowvram mode because your GPU seems to have 4GB or less. If you don't want this use: --normalvram")
            set_vram_to = VRAMState.LOW_VRAM
        elif total_vram > total_ram * 1.1 and total_vram > 14336:
            print("Enabling highvram mode because your GPU has more vram than your computer has ram. If you don't want this use: --normalvram")
            vram_state = VRAMState.HIGH_VRAM
except:
    pass

try:
    OOM_EXCEPTION = torch.cuda.OutOfMemoryError
except:
    OOM_EXCEPTION = Exception

XFORMERS_VERSION = ""
XFORMERS_ENABLED_VAE = True
if args.disable_xformers:
    XFORMERS_IS_AVAILABLE = False
else:
    try:
        import xformers
        import xformers.ops
        XFORMERS_IS_AVAILABLE = True
        try:
            XFORMERS_VERSION = xformers.version.__version__
            print("xformers version:", XFORMERS_VERSION)
            if XFORMERS_VERSION.startswith("0.0.18"):
                print()
                # print("WARNING: This version of xformers has a major bug where you will get black images when generating high resolution images.")
                # print("Please downgrade or upgrade xformers to a different version.")
                # print()
                # XFORMERS_ENABLED_VAE = False
        except:
            pass
    except:
        XFORMERS_IS_AVAILABLE = False

ENABLE_PYTORCH_ATTENTION = args.use_pytorch_cross_attention
if ENABLE_PYTORCH_ATTENTION:
    torch.backends.cuda.enable_math_sdp(True)
    torch.backends.cuda.enable_flash_sdp(True)
    torch.backends.cuda.enable_mem_efficient_sdp(True)
    XFORMERS_IS_AVAILABLE = False

if args.lowvram:
    set_vram_to = VRAMState.LOW_VRAM
elif args.novram:
    set_vram_to = VRAMState.NO_VRAM
elif args.highvram:
    vram_state = VRAMState.HIGH_VRAM

FORCE_FP32 = False
if args.force_fp32:
    print("Forcing FP32, if this improves things please report it.")
    FORCE_FP32 = True


if set_vram_to in (VRAMState.LOW_VRAM, VRAMState.NO_VRAM):
    try:
        import accelerate
        accelerate_enabled = True
        vram_state = set_vram_to
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        print("ERROR: COULD NOT ENABLE LOW VRAM MODE.")

    total_vram_available_mb = (total_vram - 1024) // 2
    total_vram_available_mb = int(max(256, total_vram_available_mb))

try:
    if torch.backends.mps.is_available():
        vram_state = VRAMState.MPS
except:
    pass

if args.cpu:
    vram_state = VRAMState.CPU

# print(f"Set vram state to: {vram_state.name}")


class ModelManager:
    _instance = None
    _initialised = False
    _load_mutex = threading.RLock()
    _property_mutex = threading.RLock()
    sampler_mutex = threading.RLock()
    vae_mutex = threading.RLock()

    _property_mutex = nullcontext()

    user_reserved_vram_mb = 0

    # We are a singleton
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # We initialise only ever once (in the lifetime of the singleton)
    def __init__(self):
        if not self._initialised:
            self.models_in_use = []
            self.current_loaded_models = []
            self.current_gpu_controlnets = []
            self.models_accelerated = []
            self.__class__._initialised = True    

    def set_user_reserved_vram(self, vram_mb):
        with self._property_mutex:
            self.user_reserved_vram_mb = vram_mb

    def get_models_on_gpu(self):
        with self._property_mutex:
            return self.current_loaded_models[:]

    def set_model_in_use(self, model):
        with self._property_mutex:
            self.models_in_use.append(model)

    def is_model_in_use(self, model):
        with self._property_mutex:
            return model in self.models_in_use

    def unload_model(self, model):
        global vram_state
        with self._property_mutex:
            if model not in self.current_loaded_models:
                logger.debug("Skip GPU unload as not on the GPU")
                return

            if model in self.models_in_use:
                logger.debug("Not unloaded model as it is in use right now")
                return

            if model in self.models_accelerated:
                accelerate.hooks.remove_hook_from_submodules(model.model)
                self.models_accelerated.remove(model)

            self.current_loaded_models.remove(model)

        # Unload to RAM
        model.model.cpu()
        model.unpatch_model()
        return True

    def done_with_model(self, model):
        with self._property_mutex:
            if model in self.models_in_use:
                self.models_in_use.remove(model)

    def load_model_gpu(self, model):
        global vram_state
        
        with self._load_mutex:
            #logger.warning(f"load_model_gpu( {id(model):x} )")

            # Don't run out of vram
            if self.current_loaded_models:
                freemem = round(get_free_memory(get_torch_device()) / (1024 * 1024))
                logger.debug(f"Free VRAM is: {freemem}MB ({len(self.current_loaded_models)} models loaded on GPU)")
                if freemem < self.user_reserved_vram_mb:
                    # Release the first least used model that we can
                    for release_model in reversed(self.current_loaded_models):
                        if self.unload_model(release_model):
                            break
                    freemem = round(get_free_memory(get_torch_device()) / (1024 * 1024))
                    logger.debug(f"Unloaded a model, free VRAM is now: {freemem}MB ({len(self.current_loaded_models)} models loaded on GPU)")

            if model in self.current_loaded_models:
                # Move this model to the top of the list
                self.current_loaded_models.insert(0, self.current_loaded_models.pop(self.current_loaded_models.index(model)))
                #logger.warning(f"Model {id(model):x} already on GPU so not loading")
                return model
            
            try:
                #logger.warning(f"Patching model {id(model):x}")
                real_model = model.patch_model()
            except Exception as e:
                logger.error("Patching failed")
                model.unpatch_model()
                raise e
            
            #logger.warning(f"Adding model to current_loaded_models {id(model):x}")
            self.current_loaded_models.insert(0, model)

            if vram_state == VRAMState.CPU:
                pass
            elif vram_state == VRAMState.MPS:
                mps_device = torch.device("mps")
                real_model.to(mps_device)
            elif vram_state == VRAMState.NORMAL_VRAM or vram_state == VRAMState.HIGH_VRAM:
                if model in self.models_accelerated:
                    #logger.warning(f"removing model from accelerated list {id(model):x}")
                    self.models_accelerated.remove(model)
                #logger.warning(f"Moving model {id(model):x} / {id(real_model):x} to device {get_torch_device()}")
                real_model.to(get_torch_device())
                #logger.warning(f"Done moving model {id(model):x} / {id(real_model):x} to device {get_torch_device()}")
            else:
                if vram_state == VRAMState.NO_VRAM:
                    device_map = accelerate.infer_auto_device_map(real_model, max_memory={0: "256MiB", "cpu": "16GiB"})
                elif vram_state == VRAMState.LOW_VRAM:
                    device_map = accelerate.infer_auto_device_map(real_model, max_memory={0: "{}MiB".format(total_vram_available_mb), "cpu": "16GiB"})

                accelerate.dispatch_model(real_model, device_map=device_map, main_device=get_torch_device())
                self.models_accelerated.append(model)
            return model

    def load_controlnet_gpu(self, control_models):
        with self._load_mutex:
            global vram_state
            if vram_state == VRAMState.CPU:
                return

            if vram_state == VRAMState.LOW_VRAM or vram_state == VRAMState.NO_VRAM:
                #don't load controlnets like this if low vram because they will be loaded right before running and unloaded right after
                return

            models = []
            for m in control_models:
                models += m.get_models()

            device = get_torch_device()
            for m in models:
                if m not in self.current_gpu_controlnets:
                    #logger.warning(f"Loaded controlnet {id(m):x} to GPU")
                    self.current_gpu_controlnets.append(m.to(device))

    def unload_controlnet_gpu(self, control_models):
        with self._load_mutex:
            global vram_state
            if vram_state == VRAMState.CPU:
                return

            if vram_state == VRAMState.LOW_VRAM or vram_state == VRAMState.NO_VRAM:
                #don't load controlnets like this if low vram because they will be loaded right before running and unloaded right after
                return

            models = []
            for m in control_models:
                models += m.get_models()

            for m in models:
                if m in self.current_gpu_controlnets:
                    m.cpu()
                    self.current_gpu_controlnets.remove(m)
                    del m

model_manager = ModelManager()


def load_if_low_vram(model):
    global vram_state
    if vram_state == VRAMState.LOW_VRAM or vram_state == VRAMState.NO_VRAM:
        return model.to(get_torch_device())
    return model

def unload_if_low_vram(model):
    global vram_state
    if vram_state == VRAMState.LOW_VRAM or vram_state == VRAMState.NO_VRAM:
        return model.cpu()
    return model

def get_torch_device():
    global xpu_available
    if vram_state == VRAMState.MPS:
        return torch.device("mps")
    if vram_state == VRAMState.CPU:
        return torch.device("cpu")
    else:
        if xpu_available:
            return torch.device("xpu")
        else:
            return torch.cuda.current_device()

def get_autocast_device(dev):
    if hasattr(dev, 'type'):
        return dev.type
    return "cuda"


def xformers_enabled():
    if vram_state == VRAMState.CPU:
        return False
    return XFORMERS_IS_AVAILABLE


def xformers_enabled_vae():
    enabled = xformers_enabled()
    if not enabled:
        return False

    return XFORMERS_ENABLED_VAE

def pytorch_attention_enabled():
    return ENABLE_PYTORCH_ATTENTION

def get_free_memory(dev=None, torch_free_too=False):
    global xpu_available
    if dev is None:
        dev = get_torch_device()

    if hasattr(dev, 'type') and (dev.type == 'cpu' or dev.type == 'mps'):
        mem_free_total = psutil.virtual_memory().available
        mem_free_torch = mem_free_total
    else:
        if xpu_available:
            mem_free_total = torch.xpu.get_device_properties(dev).total_memory - torch.xpu.memory_allocated(dev)
            mem_free_torch = mem_free_total
        else:
            stats = torch.cuda.memory_stats(dev)
            mem_active = stats['active_bytes.all.current']
            mem_reserved = stats['reserved_bytes.all.current']
            mem_free_cuda, _ = torch.cuda.mem_get_info(dev)
            mem_free_torch = mem_reserved - mem_active
            mem_free_total = mem_free_cuda + mem_free_torch

    if torch_free_too:
        return (mem_free_total, mem_free_torch)
    else:
        return mem_free_total

def maximum_batch_area():
    return 0
    # See https://github.com/jug-dev/hordelib/issues/225
    global vram_state
    if vram_state == VRAMState.NO_VRAM:
        return 0

    memory_free = get_free_memory() / (1024 * 1024)
    area = ((memory_free - 1024) * 0.9) / (0.6)
    return int(max(area, 0))

def cpu_mode():
    global vram_state
    return vram_state == VRAMState.CPU

def mps_mode():
    global vram_state
    return vram_state == VRAMState.MPS

def should_use_fp16():
    global xpu_available
    if FORCE_FP32:
        return False

    if cpu_mode() or mps_mode() or xpu_available:
        return False #TODO ?

    if torch.cuda.is_bf16_supported():
        return True

    props = torch.cuda.get_device_properties("cuda")
    if props.major < 7:
        return False

    #FP32 is faster on those cards?
    nvidia_16_series = ["1660", "1650", "1630", "T500", "T550", "T600"]
    for x in nvidia_16_series:
        if x in props.name:
            return False

    return True

def soft_empty_cache():
    global xpu_available
    if xpu_available:
        torch.xpu.empty_cache()
    elif torch.cuda.is_available():
        if torch.version.cuda: #This seems to make things worse on ROCm so I only do it for cuda
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()

#TODO: might be cleaner to put this somewhere else
import threading

class InterruptProcessingException(Exception):
    pass

interrupt_processing_mutex = threading.RLock()

interrupt_processing = False
def interrupt_current_processing(value=True):
    global interrupt_processing
    global interrupt_processing_mutex
    with interrupt_processing_mutex:
        interrupt_processing = value

def processing_interrupted():
    global interrupt_processing
    global interrupt_processing_mutex
    with interrupt_processing_mutex:
        return interrupt_processing

def throw_exception_if_processing_interrupted():
    global interrupt_processing
    global interrupt_processing_mutex
    with interrupt_processing_mutex:
        if interrupt_processing:
            interrupt_processing = False
            raise InterruptProcessingException()
