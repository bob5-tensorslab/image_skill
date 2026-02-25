import requests
import os
from datetime import datetime
import logging
import yaml
import time

logger = logging.getLogger(__name__)

def download_image(image_url: str, target_image_name: str= None, save_dir: str= None) -> str:
    os.makedirs(save_dir, exist_ok=True)

    response = requests.get(image_url, proxies={"http": None, "https": None})
    if response.status_code == 200:
        if target_image_name:
            target_image_name = target_image_name.split(".")[0] + "."+ os.path.basename(image_url).split(".")[-1]
            image_path = os.path.join(save_dir, target_image_name)
        else:
            image_path = os.path.join(save_dir, image_url.split("/")[-1])
        with open(image_path, "wb") as f:
            f.write(response.content)
        return image_path
    raise Exception(f"Failed to download image from {image_url}")

def upload_image_with_cache(image_path, subfolder="drawer_agent", upload_type="input", host_url=None, save_dir=None):
    """
    带缓存的上传图片方法，避免重复上传
    :param image_path: 本地图片路径
    :param subfolder: 子文件夹名称
    :param upload_type: 上传类型，默认为"input"
    :param save_dir: 项目路径，如果提供，则使用项目路径作为缓存目录,及comfy input中子路径
    :return: 返回格式为 "subfolder/filename" 的字符串，失败返回None
    """
    # 检查文件是否存在
    if not image_path.startswith("http") and not os.path.exists(image_path):
        logger.error(f"文件不存在: {image_path}")
        raise Exception(f"文件不存在: {image_path}")

    os.makedirs(save_dir, exist_ok=True)
    cache_file = os.path.join(save_dir, "comfy_upload_cache.yml")
    # 加载缓存
    cache_data = {}
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"加载缓存文件失败: {e}")
            cache_data = {}

    # 检查是否已上传
    if image_path in cache_data:
        cached_result = cache_data[image_path]
        logger.info(f"文件已上传过，直接返回缓存结果: {cached_result['result']}")
        return cached_result['result']

    # 执行上传
    subfolder = save_dir if save_dir else subfolder
    result = _upload_image(image_path, subfolder, upload_type, host_url, save_dir)

    # 保存到缓存
    if result:
        cache_data[image_path] = {
            'result': result,
            'upload_time': datetime.now().isoformat(),
            'subfolder': subfolder,
            'upload_type': upload_type
        }

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                yaml.dump(cache_data, f, default_flow_style=False,
                          allow_unicode=True)
            logger.info(f"上传结果已缓存: {result}")
        except Exception as e:
            logger.warning(f"保存缓存失败: {e}")

    return result


def add_prompt(url, prompt):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json", }
    ret = requests.post(url, data=str(prompt).encode(
        "utf-8"), timeout=30, headers=headers, proxies={"http": None, "https": None})
    logger.info(ret)
    logger.info(ret.text)
    result = ret.json()
    node_errors = result.get("node_errors", {})
    if len(node_errors) > 0:
        logger.error(f"node_errors: {node_errors}")
        raise Exception(f"submit prompt failed, node_errors: {node_errors}")
    return result.get("prompt_id")


def _upload_image(image_path, subfolder="kontext", upload_type="input", host_url=None, save_dir=None):
    """
    上传图片到ComfyUI服务器
    :param image_path: 本地图片路径或HTTP URL
    :param subfolder: 子文件夹名称
    :param upload_type: 上传类型，默认为"input"
    :return: 返回格式为 "subfolder/filename" 的字符串，失败返回None
    """
    try:
        # 判断是否为HTTP URL
        is_url = image_path.startswith(
            'http://') or image_path.startswith('https://')

        if is_url:
            # 从URL下载图片
            logger.info(f"从URL下载图片: {image_path}")
            image_path = download_image(image_path, save_dir=save_dir)

        # 检查本地文件是否存在
        if not os.path.exists(image_path):
            logger.error(f"文件不存在: {image_path}")
            return None

        # 获取文件名
        filename = os.path.basename(image_path)

        # 读取本地文件
        with open(image_path, 'rb') as f:
            image_data = f.read()

        upload_url = f"{host_url}/upload/image"

        # 准备文件数据
        files = {
            'image': (filename, image_data, 'image/jpeg')
        }
        data = {
            'type': upload_type,
            'subfolder': subfolder
        }
        logger.info(f"上传到: {upload_url}")

        # 发送上传请求
        response = requests.post(
            upload_url, files=files, data=data, timeout=30, proxies={"http": None, "https": None})

        if response.status_code == 200:
            result = response.json()
            # 返回 subfolder/filename 格式
            if result.get('subfolder'):
                return f"{result['subfolder']}/{result['name']}"
            else:
                return result['name']
        else:
            logger.error(f"上传失败，状态码: {response.status_code}")
            logger.error(f"响应内容: {response.text}")
            raise Exception(
                f"上传失败，状态码: {response.status_code}, 响应内容: {response.text}")

    except Exception as e:
        logger.error(f"上传过程中发生错误: {str(e)}")
        raise Exception(f"上传过程中发生错误: {str(e)}")


def query_comfy_task(task_id, max_wait_time, result_file_name=None, host_url=None, save_dir=None):
    logger.info(
        f"fetch_generated_image, host_url: {host_url}, task_id: {task_id}, max_wait_time: {max_wait_time}")
    start_time = time.time()
    # 轮询队列状态，等待任务完成
    while time.time() - start_time < max_wait_time:
        status = {}
        try:
            # 查询队列状态
            queue_response = requests.get(f"{host_url}/queue", timeout=10, proxies={"http": None, "https": None})
            queue_response.raise_for_status()
            queue_data = queue_response.json()

            # 检查任务是否还在运行队列中
            running_tasks = [task[1]
                             for task in queue_data.get("queue_running", [])]
            pending_tasks = [task[1]
                             for task in queue_data.get("queue_pending", [])]
            if task_id in running_tasks or task_id in pending_tasks:
                logger.debug(
                    f"task {task_id} is {'running' if task_id in running_tasks else 'pending' }")
                time.sleep(0.2)
                continue

            # 任务已完成，查询历史记录
            history_response = requests.get(
                f"{host_url}/history/{task_id}", timeout=10, proxies={"http": None, "https": None})
            history_response.raise_for_status()
            history_data = history_response.json()

            task_info = history_data.get(task_id, {})
            status = task_info.get("status", {})
        except requests.RequestException as e:
            logger.error(f"请求错误: {e}")
            time.sleep(0.5)
            continue
        except Exception as e:
            logger.exception(e)

        logger.info(f"task {task_id} completed, status_str: {status.get('status_str', '')}, completed: {status.get('completed', False)}")
        # 检查任务状态
        if status.get("status_str") == "success" and status.get("completed", False):
            # 获取输出图片信息
            outputs = task_info.get("outputs", {})
            save_path, result_info = None, None
            for output_id, output_data in outputs.items():
                if "text" in output_data:
                    result_info = output_data.get("text")[0]
                images = output_data.get("images", [])
                for image in images:
                    filename = image.get("filename")
                    subfolder = image.get("subfolder", "")

                    if filename:
                        # 下载图片
                        download_url = f"{host_url}/view?filename={filename}&type=output&subfolder={subfolder}"
                        image_response = requests.get(download_url, timeout=30, proxies={"http": None, "https": None})
                        image_response.raise_for_status()

                        # 确保目录存在
                        save_dir = "data/temp" if not save_dir else save_dir
                        os.makedirs(save_dir, exist_ok=True)

                        # 保存图片
                        save_path = os.path.join(save_dir, result_file_name)
                        with open(save_path, "wb") as f:
                            f.write(image_response.content)
                        
            
            return save_path, result_info

        else:
            # 尝试从status中提取错误信息
            error_message = f"task {task_id} is not success, generate image failed"
            
            # 检查是否有详细的错误信息
            if status.get("status_str") == "error":
                messages = status.get("messages", [])
                for message in messages:
                    if len(message) >= 2 and message[0] == "execution_error":
                        error_data = message[1]
                        exception_message = error_data.get("exception_message", "")
                        exception_type = error_data.get("exception_type", "")
                        node_type = error_data.get("node_type", "")
                        
                        if exception_message:
                            error_message = f"ComfyUI执行错误 - 节点类型: {node_type}, 异常类型: {exception_type}, 错误信息: {exception_message}"
                            break
            
            logger.error(error_message)
            raise Exception(error_message)
