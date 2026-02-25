import argparse
import json
import os
import random
import uuid
import logging
from comfy_tool import upload_image_with_cache, add_prompt, query_comfy_task

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

HOST_URL = os.getenv("HOST_URL", "http://10.168.1.168:8189")

ASPECT_RATIOS = {
    "1:1": (1, 1),
    "4:3": (4, 3),
    "3:4": (3, 4),
    "16:9": (16, 9),
    "9:16": (9, 16),
    "3:2": (3, 2),
    "2:3": (2, 3),
    "21:9": (21, 9),
    "9:21": (9, 21),
}

RESOLUTIONS = {
    "1k": 1024 * 1024,
    "2k": 2048 * 1536,
    "4k": 4096 * 2160,
}

image_edit_prompt_template = '''
{
	"76": {
		"inputs": {
			"image": "ScreenShot_2026-01-18_172658_739.png",
			"enabled": true,
			"input_image_path": ""
		},
		"class_type": "LoadImageWithoutListDir",
		"_meta": {
			"title": "First Image"
		}
	},
	"94": {
		"inputs": {
			"filename_prefix": "Flux2-Klein",
			"filename_suffix": "jpg",
			"grayscale": false,
			"images": [
				"103",
				0
			]
		},
		"class_type": "SaveImage",
		"_meta": {
			"title": "Save Image"
		}
	},
	"99": {
		"inputs": {
			"sampler_name": "euler"
		},
		"class_type": "KSamplerSelect",
		"_meta": {
			"title": "KSamplerSelect"
		}
	},
	"100": {
		"inputs": {
			"steps": 4,
			"width": [
				"118",
				0
			],
			"height": [
				"118",
				1
			]
		},
		"class_type": "Flux2Scheduler",
		"_meta": {
			"title": "Flux2Scheduler"
		}
	},
	"101": {
		"inputs": {
			"cfg": 1,
			"model": [
				"105",
				0
			],
			"positive": [
				"133",
				0
			],
			"negative": [
				"132",
				0
			]
		},
		"class_type": "CFGGuider",
		"_meta": {
			"title": "CFGGuider"
		}
	},
	"102": {
		"inputs": {
			"noise": [
				"104",
				0
			],
			"guider": [
				"101",
				0
			],
			"sampler": [
				"99",
				0
			],
			"sigmas": [
				"100",
				0
			],
			"latent_image": [
				"114",
				0
			]
		},
		"class_type": "SamplerCustomAdvanced",
		"_meta": {
			"title": "SamplerCustomAdvanced"
		}
	},
	"103": {
		"inputs": {
			"samples": [
				"102",
				0
			],
			"vae": [
				"108",
				0
			]
		},
		"class_type": "VAEDecode",
		"_meta": {
			"title": "VAE Decode"
		}
	},
	"104": {
		"inputs": {
			"noise_seed": 106126993014118
		},
		"class_type": "RandomNoise",
		"_meta": {
			"title": "RandomNoise"
		}
	},
	"105": {
		"inputs": {
			"unet_name": "flux-2-klein-4b-fp8.safetensors",
			"weight_dtype": "default"
		},
		"class_type": "UNETLoader",
		"_meta": {
			"title": "Load Diffusion Model"
		}
	},
	"106": {
		"inputs": {
			"clip_name": "qwen_3_4b.safetensors",
			"type": "flux2",
			"device": "default"
		},
		"class_type": "CLIPLoader",
		"_meta": {
			"title": "Load CLIP"
		}
	},
	"107": {
		"inputs": {
			"text": "将第一个图的标志应用到第二个图的包上,让女士拿着这个包",
			"clip": [
				"106",
				0
			]
		},
		"class_type": "CLIPTextEncode",
		"_meta": {
			"title": "CLIP Text Encode (Positive Prompt)"
		}
	},
	"108": {
		"inputs": {
			"vae_name": "flux2-vae.safetensors"
		},
		"class_type": "VAELoader",
		"_meta": {
			"title": "Load VAE"
		}
	},
	"109": {
		"inputs": {
			"upscale_method": "nearest-exact",
			"megapixels": 1,
			"resolution_steps": 1,
			"image": [
				"76",
				0
			]
		},
		"class_type": "ImageScaleToTotalPixels",
		"_meta": {
			"title": "ImageScaleToTotalPixels"
		}
	},
	"112": {
		"inputs": {
			"conditioning": [
				"107",
				0
			]
		},
		"class_type": "ConditioningZeroOut",
		"_meta": {
			"title": "ConditioningZeroOut"
		}
	},
	"114": {
		"inputs": {
			"width": [
				"118",
				0
			],
			"height": [
				"118",
				1
			],
			"batch_size": [
				"118",
				2
			]
		},
		"class_type": "EmptyFlux2LatentImage",
		"_meta": {
			"title": "Empty Flux 2 Latent"
		}
	},
	"118": {
		"inputs": {
			"aspect_ratio": "auto",
			"size": "1k",
			"divisible_by": "16",
			"batch_size": [
				"119",
				2
			],
			"input_width": [
				"119",
				0
			],
			"input_height": [
				"119",
				1
			]
		},
		"class_type": "AspectRatioSizeNodeOfUtils",
		"_meta": {
			"title": "Aspect Ratio Size Selector"
		}
	},
	"119": {
		"inputs": {
			"image": [
				"128",
				0
			]
		},
		"class_type": "GetImageSize",
		"_meta": {
			"title": "Get Image Size"
		}
	},
	"120": {
		"inputs": {
			"enabled": [
				"126",
				2
			],
			"pixels": [
				"123",
				0
			],
			"vae": [
				"108",
				0
			]
		},
		"class_type": "VAEEncoderSwitch",
		"_meta": {
			"title": "VAE Encoder (Switch)"
		}
	},
	"123": {
		"inputs": {
			"upscale_method": "nearest-exact",
			"megapixels": 1,
			"resolution_steps": 1,
			"enabled": [
				"126",
				2
			],
			"image": [
				"126",
				0
			]
		},
		"class_type": "ImageScaleToTotalPixelsSwitch",
		"_meta": {
			"title": "ImageScaleToTotalPixelsSwitch"
		}
	},
	"124": {
		"inputs": {
			"enabled": [
				"126",
				2
			],
			"conditioning": [
				"115:77",
				0
			],
			"latent": [
				"120",
				0
			]
		},
		"class_type": "ReferenceLatentSwitch",
		"_meta": {
			"title": "ReferenceLatentSwitch"
		}
	},
	"126": {
		"inputs": {
			"image": "ScreenShot_2026-01-18_172632_900.png",
			"enabled": false,
			"input_image_path": ""
		},
		"class_type": "LoadImageWithoutListDir",
		"_meta": {
			"title": "Second Image"
		}
	},
	"127": {
		"inputs": {
			"enabled": [
				"126",
				2
			],
			"conditioning": [
				"115:76",
				0
			],
			"latent": [
				"120",
				0
			]
		},
		"class_type": "ReferenceLatentSwitch",
		"_meta": {
			"title": "ReferenceLatentSwitch"
		}
	},
	"128": {
		"inputs": {
			"image_prior": [
				"130",
				0
			],
			"image_alternative": [
				"123",
				0
			],
			"image_third": [
				"109",
				0
			]
		},
		"class_type": "ImageAutoSelector",
		"_meta": {
			"title": "Image Auto Selector"
		}
	},
	"129": {
		"inputs": {
			"image": "result_image_edit_results_nobg_work_uqYw_b949e8a0998d4eaa8f805beea0f15074.png",
			"enabled": false,
			"input_image_path": ""
		},
		"class_type": "LoadImageWithoutListDir",
		"_meta": {
			"title": "The Third Image"
		}
	},
	"130": {
		"inputs": {
			"upscale_method": "nearest-exact",
			"megapixels": 1,
			"resolution_steps": 1,
			"enabled": [
				"129",
				2
			],
			"image": [
				"129",
				0
			]
		},
		"class_type": "ImageScaleToTotalPixelsSwitch",
		"_meta": {
			"title": "ImageScaleToTotalPixelsSwitch"
		}
	},
	"131": {
		"inputs": {
			"enabled": [
				"129",
				2
			],
			"pixels": [
				"130",
				0
			],
			"vae": [
				"108",
				0
			]
		},
		"class_type": "VAEEncoderSwitch",
		"_meta": {
			"title": "VAE Encoder (Switch)"
		}
	},
	"132": {
		"inputs": {
			"enabled": [
				"129",
				2
			],
			"conditioning": [
				"127",
				0
			],
			"latent": [
				"131",
				0
			]
		},
		"class_type": "ReferenceLatentSwitch",
		"_meta": {
			"title": "ReferenceLatentSwitch"
		}
	},
	"133": {
		"inputs": {
			"enabled": [
				"129",
				2
			],
			"conditioning": [
				"124",
				0
			],
			"latent": [
				"131",
				0
			]
		},
		"class_type": "ReferenceLatentSwitch",
		"_meta": {
			"title": "ReferenceLatentSwitch"
		}
	},
	"115:78": {
		"inputs": {
			"pixels": [
				"109",
				0
			],
			"vae": [
				"108",
				0
			]
		},
		"class_type": "VAEEncode",
		"_meta": {
			"title": "VAE Encode"
		}
	},
	"115:77": {
		"inputs": {
			"conditioning": [
				"107",
				0
			],
			"latent": [
				"115:78",
				0
			]
		},
		"class_type": "ReferenceLatent",
		"_meta": {
			"title": "ReferenceLatent"
		}
	},
	"115:76": {
		"inputs": {
			"conditioning": [
				"112",
				0
			],
			"latent": [
				"115:78",
				0
			]
		},
		"class_type": "ReferenceLatent",
		"_meta": {
			"title": "ReferenceLatent"
		}
	}
}
'''


def _process_single_image_edit_task(image_path: str, edit_word: str, host_url: str, 
                                           result_filename: str, result_dir: str,
                                           aspect_ratio: str = "auto"):
    prompt = json.loads(image_edit_prompt_template)
    task_id = str(uuid.uuid4())
    
    uploaded_image = upload_image_with_cache(
        image_path, 
        subfolder="image_edit", 
        host_url=host_url, 
        save_dir=result_dir
    )
    
    noise_seed = random.randint(1, 999999999999999)
    
    prompt["76"]["inputs"]["image"] = uploaded_image
    prompt["107"]["inputs"]["text"] = edit_word
    prompt["104"]["inputs"]["noise_seed"] = noise_seed
    prompt["94"]["inputs"]["filename_prefix"] = f"image_edit/{task_id}"    

    if aspect_ratio.lower() != "auto":
        prompt["118"]["inputs"]["aspect_ratio"] = aspect_ratio
    
    prompt_obj = {
        "prompt": prompt,
        "prompt_id": task_id,
        "client_id": task_id
    }
    
    prompt_result = json.dumps(prompt_obj)
    add_prompt(f"{host_url}/prompt", prompt_result)
    
    logger.info(f"提交编辑任务成功: image={uploaded_image}, edit_word={edit_word}, task_id={task_id}")
    
    logger.info(f"开始查询任务结果，任务ID: {task_id}")
    local_path, result_info = query_comfy_task(
        task_id=task_id,
        max_wait_time=120,
        result_file_name=result_filename,
        host_url=host_url,
        save_dir=result_dir
    )
    
    return local_path, result_info


def change_aspect_ratio(image_path: str, aspect_ratio: str, host_url: str = HOST_URL,
                        result_dir: str = "result/image_edit_results",
                        result_filename: str = None):
    """
    变宽高比功能：保持图片内容不变，改变宽高比
    """
    if aspect_ratio not in ASPECT_RATIOS and aspect_ratio != "auto":
        raise ValueError(f"不支持的宽高比: {aspect_ratio}，可选: {list(ASPECT_RATIOS.keys())}")
    
    edit_word = "Keep the image content unchanged, maintain all visual elements, only change the aspect ratio"
    
    if result_filename is None:
        result_filename = f"aspect_ratio_{os.path.basename(image_path)}"
    
    return _process_single_image_edit_task(
        image_path=image_path,
        edit_word=edit_word,
        host_url=host_url,
        result_filename=result_filename,
        result_dir=result_dir,
        aspect_ratio=aspect_ratio
    )


def erase_object(image_path: str, target_object: str, host_url: str = HOST_URL,
                 result_dir: str = "result/image_edit_results",
                 result_filename: str = None):
    """
    擦除功能：移除图片中的指定对象
    """
    edit_word = f"Keep all other parts unchanged, remove the {target_object} from the image"
    
    if result_filename is None:
        result_filename = f"erase_{os.path.basename(image_path)}"
    
    return _process_single_image_edit_task(
        image_path=image_path,
        edit_word=edit_word,
        host_url=host_url,
        result_filename=result_filename,
        result_dir=result_dir
    )


def remove_background(image_path: str, host_url: str = HOST_URL,
                      result_dir: str = "result/image_edit_results",
                      result_filename: str = None):
    """
    去背景功能：移除图片背景
    """
    edit_word = "Remove the background completely, keep only the main subject, make the background transparent or white"
    
    if result_filename is None:
        result_filename = f"nobg_{os.path.basename(image_path)}"
    
    return _process_single_image_edit_task(
        image_path=image_path,
        edit_word=edit_word,
        host_url=host_url,
        result_filename=result_filename,
        result_dir=result_dir
    )


def general_edit(image_path: str, edit_word: str, host_url: str = HOST_URL,
                 result_dir: str = "result/image_edit_results",
                 result_filename: str = None,
                 aspect_ratio: str = "auto"):
    """
    通用编辑功能：接收自定义编辑指令
    """
    if aspect_ratio not in ASPECT_RATIOS and aspect_ratio != "auto":
        raise ValueError(f"不支持的宽高比: {aspect_ratio}，可选: {list(ASPECT_RATIOS.keys()) + ['auto']}")
    
    if result_filename is None:
        result_filename = f"edit_{os.path.basename(image_path)}"
    
    return _process_single_image_edit_task(
        image_path=image_path,
        edit_word=edit_word,
        host_url=host_url,
        result_filename=result_filename,
        result_dir=result_dir,
        aspect_ratio=aspect_ratio
    )


def main():
    parser = argparse.ArgumentParser(description="Image Edit Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    parser.add_argument("--host", default=HOST_URL, help="ComfyUI host URL")
    parser.add_argument("--output-dir", default="result/image_edit_results", help="Output directory")
    parser.add_argument("--output-name", default=None, help="Output filename")
    
    aspect_parser = subparsers.add_parser("aspect", help="Change image aspect ratio")
    aspect_parser.add_argument("image", help="Input image path")
    aspect_parser.add_argument("ratio", choices=list(ASPECT_RATIOS.keys()), help="Target aspect ratio")
    
    erase_parser = subparsers.add_parser("erase", help="Erase object from image")
    erase_parser.add_argument("image", help="Input image path")
    erase_parser.add_argument("target", help="Object to erase")
    
    bg_parser = subparsers.add_parser("rmbg", help="Remove image background")
    bg_parser.add_argument("image", help="Input image path")
    
    edit_parser = subparsers.add_parser("edit", help="General image editing")
    edit_parser.add_argument("image", help="Input image path")
    edit_parser.add_argument("prompt", help="Edit prompt/instruction")
    edit_parser.add_argument("--ratio", default="auto", help="Aspect ratio (optional)")
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    host_url = args.host
    result_dir = args.output_dir
    result_filename = args.output_name
    
    if args.command == "aspect":
        local_path, result_info = change_aspect_ratio(
            image_path=args.image,
            aspect_ratio=args.ratio,
            host_url=host_url,
            result_dir=result_dir,
            result_filename=result_filename
        )
        logger.info(f"变宽高比完成: {local_path}")
        
    elif args.command == "erase":
        local_path, result_info = erase_object(
            image_path=args.image,
            target_object=args.target,
            host_url=host_url,
            result_dir=result_dir,
            result_filename=result_filename
        )
        logger.info(f"擦除完成: {local_path}")
        
    elif args.command == "rmbg":
        local_path, result_info = remove_background(
            image_path=args.image,
            host_url=host_url,
            result_dir=result_dir,
            result_filename=result_filename
        )
        logger.info(f"去背景完成: {local_path}")
        
    elif args.command == "edit":
        local_path, result_info = general_edit(
            image_path=args.image,
            edit_word=args.prompt,
            host_url=host_url,
            result_dir=result_dir,
            result_filename=result_filename,
            aspect_ratio=args.ratio
        )
        logger.info(f"编辑完成: {local_path}")


if __name__ == "__main__":
    main()
