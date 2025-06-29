import subprocess
import platform
import yaml
import logging
import os

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GeminiRouter:
    """
    命令路由器，负责将自然语言请求转换为系统命令。
    它首先尝试使用本地的命令词典进行匹配，如果失败，则调用 Gemini CLI。
    """
    def __init__(self, config_path='configs/config.yaml'):
        """
        初始化路由器，加载配置和本地命令词典。
        Args:
            config_path (str): 配置文件的路径。
        """
        self.config = self._load_config(config_path)
        self.local_command_map = {
            "列出文件": "dir" if platform.system() == "Windows" else "ls",
            "显示当前路径": "cd" if platform.system() == "Windows" else "pwd",
            "创建文件夹": "mkdir",
            # 示例：创建一个名为 'test' 的文件夹 -> mkdir test
        }

    def _load_config(self, config_path: str) -> dict:
        """
        加载 YAML 配置文件。
        Args:
            config_path: 配置文件的路径。
        Returns:
            包含配置信息的字典。
        """
        try:
            # 确保路径在不同操作系统下都能正确解析
            absolute_path = os.path.abspath(config_path)
            with open(absolute_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logging.warning(f"配置文件 {config_path} 未找到，将使用默认设置。")
            return {'use_gemini': False, 'gemini_timeout': 15}
        except Exception as e:
            logging.error(f"加载配置文件时出错: {e}")
            return {'use_gemini': False, 'gemini_timeout': 15}

    def nl_to_command(self, user_input: str) -> str:
        """
        将自然语言输入转换为 shell 命令。

        Args:
            user_input: 用户的自然语言输入。

        Returns:
            转换后的 shell 命令，如果失败则返回空字符串。
        """
        # 1. 尝试本地词典匹配
        for keyword, command_template in self.local_command_map.items():
            if user_input.startswith(keyword):
                # 如果命令需要参数（例如 '创建文件夹 demo'）
                parts = user_input.split(keyword, 1)
                if len(parts) > 1 and parts[1].strip():
                    # 提取参数
                    args = parts[1].strip()
                    return f"{command_template} {args}"
                else:
                    # 对于没有参数的命令
                    return command_template

        # 2. 如果本地匹配失败，并且启用了 Gemini，则调用 Gemini CLI
        if self.config.get('use_gemini'):
            return self._call_gemini_cli(user_input)

        # 3. 如果所有方法都失败，则返回原始输入，由安全执行器处理
        logging.info("本地词典未匹配，且未启用 Gemini，返回原始输入。")
        return user_input.strip()

    def _call_gemini_cli(self, prompt: str) -> str:
        """
        调用 Gemini CLI 将自然语言转换为命令。

        Args:
            prompt: 发送给 Gemini 的用户输入。

        Returns:
            从 Gemini 返回的命令，或者在失败时返回空字符串。
        """
        timeout = self.config.get('gemini_timeout', 15)
        command = f'gemini "{prompt}" --shell'
        logging.info(f"调用 Gemini CLI: {command}")

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True  # 如果命令返回非零退出码，则引发 CalledProcessError
            )
            # 假设 Gemini CLI 成功时返回纯 shell 命令
            shell_command = result.stdout.strip()
            logging.info(f"Gemini CLI 返回命令: '{shell_command}'")
            return shell_command
        except FileNotFoundError:
            logging.error("命令 'gemini' 未找到。请确保 Gemini CLI 已安装并已添加到系统 PATH 中。")
            return ""
        except subprocess.TimeoutExpired:
            logging.error(f"Gemini CLI 调用超时（超过 {timeout} 秒）。")
            return ""
        except subprocess.CalledProcessError as e:
            logging.error(f"Gemini CLI 调用失败，退出码 {e.returncode}。错误信息: {e.stderr.strip()}")
            return ""
        except Exception as e:
            logging.error(f"调用 Gemini CLI 时发生未知错误: {e}")
            return ""