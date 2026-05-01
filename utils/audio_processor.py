import speech_recognition as sr
from pydub import AudioSegment
from pydub.effects import normalize
import io
import wave
import tempfile
import os
from typing import Optional, Tuple, Union
import logging
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

class AudioProcessor:
    """音频处理器"""
    
    def __init__(self, language: str = "zh-CN"):
        """
        初始化音频处理器
        
        Args:
            language: 语音识别语言，默认中文
        """
        self.language = language
        self.recognizer = sr.Recognizer()
        self.supported_formats = ['.wav', '.mp3', '.m4a', '.flac', '.ogg']
    
    def convert_to_wav(self, audio_path: str, output_path: Optional[str] = None) -> str:
        """
        将音频文件转换为WAV格式
        
        Args:
            audio_path: 输入音频文件路径
            output_path: 输出WAV文件路径，如果为None则创建临时文件
        
        Returns:
            转换后的WAV文件路径
        """
        try:
            # 检查文件格式
            file_ext = Path(audio_path).suffix.lower()
            if file_ext not in self.supported_formats:
                raise ValueError(f"不支持的音频格式: {file_ext}")
            
            # 加载音频文件
            if file_ext == '.mp3':
                audio = AudioSegment.from_mp3(audio_path)
            elif file_ext == '.m4a':
                audio = AudioSegment.from_file(audio_path, format='m4a')
            elif file_ext == '.flac':
                audio = AudioSegment.from_file(audio_path, format='flac')
            elif file_ext == '.ogg':
                audio = AudioSegment.from_file(audio_path, format='ogg')
            else:
                # 已经是WAV格式
                return audio_path
            
            # 标准化音频
            audio = normalize(audio)
            
            # 设置输出路径
            if output_path is None:
                output_path = tempfile.mktemp(suffix='.wav')
            
            # 导出为WAV
            audio.export(output_path, format='wav', parameters=[
                '-ac', '1',  # 单声道
                '-ar', '16000',  # 16kHz采样率
                '-sample_fmt', 's16'  # 16位采样
            ])
            
            logger.info(f"音频转换完成: {audio_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"音频转换失败: {e}")
            raise
    
    def speech_to_text(self, audio_path: str) -> str:
        """
        语音转文本
        
        Args:
            audio_path: 音频文件路径
        
        Returns:
            识别的文本
        """
        try:
            # 转换为WAV格式
            wav_path = self.convert_to_wav(audio_path)
            
            with sr.AudioFile(wav_path) as source:
                # 调整环境噪声
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # 录制音频
                audio_data = self.recognizer.record(source)
                
                # 识别语音
                text = self.recognizer.recognize_google(
                    audio_data,
                    language=self.language
                )
            
            # 清理临时文件
            if wav_path != audio_path and os.path.exists(wav_path):
                os.remove(wav_path)
            
            logger.info(f"语音识别成功: {len(text)} 字符")
            return text
            
        except sr.UnknownValueError:
            logger.warning("无法理解音频内容")
            return ""
        except sr.RequestError as e:
            logger.error(f"语音识别服务错误: {e}")
            return ""
        except Exception as e:
            logger.error(f"语音识别失败: {e}")
            return ""
    
    def text_to_speech(self, text: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        文本转语音（需要安装gTTS或其他TTS引擎）
        
        Args:
            text: 要转换的文本
            output_path: 输出音频文件路径
        
        Returns:
            音频文件路径，如果失败则返回None
        """
        try:
            # 这里使用gTTS作为示例，需要安装：pip install gtts
            from gtts import gTTS
            
            if output_path is None:
                output_path = tempfile.mktemp(suffix='.mp3')
            
            # 创建TTS对象
            tts = gTTS(
                text=text,
                lang='zh-cn' if self.language == 'zh-CN' else 'en'
            )
            
            # 保存音频文件
            tts.save(output_path)
            
            logger.info(f"文本转语音完成: {len(text)} 字符 -> {output_path}")
            return output_path
            
        except ImportError:
            logger.error("未安装gTTS，请运行: pip install gtts")
            return None
        except Exception as e:
            logger.error(f"文本转语音失败: {e}")
            return None
    
    def extract_audio_features(self, audio_path: str) -> dict:
        """
        提取音频特征
        
        Args:
            audio_path: 音频文件路径
        
        Returns:
            音频特征字典
        """
        try:
            wav_path = self.convert_to_wav(audio_path)
            
            with wave.open(wav_path, 'rb') as wav_file:
                # 获取音频参数
                n_channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                frame_rate = wav_file.getframerate()
                n_frames = wav_file.getnframes()
                duration = n_frames / float(frame_rate)
                
                # 读取音频数据
                audio_data = wav_file.readframes(n_frames)
                
                # 转换为numpy数组
                if sample_width == 1:
                    dtype = np.uint8
                elif sample_width == 2:
                    dtype = np.int16
                elif sample_width == 4:
                    dtype = np.int32
                else:
                    raise ValueError(f"不支持的采样宽度: {sample_width}")
                
                audio_array = np.frombuffer(audio_data, dtype=dtype)
                
                # 如果是多声道，取平均值
                if n_channels > 1:
                    audio_array = audio_array.reshape(-1, n_channels).mean(axis=1)
                
                # 计算音频特征
                features = {
                    "duration": duration,
                    "sample_rate": frame_rate,
                    "channels": n_channels,
                    "sample_width": sample_width,
                    "samples": n_frames,
                    "amplitude": {
                        "max": float(np.max(audio_array)),
                        "min": float(np.min(audio_array)),
                        "mean": float(np.mean(audio_array)),
                        "std": float(np.std(audio_array))
                    },
                    "rms": float(np.sqrt(np.mean(audio_array**2))),
                    "zero_crossing_rate": float(np.sum(np.diff(np.sign(audio_array)) != 0) / len(audio_array))
                }
            
            # 清理临时文件
            if wav_path != audio_path and os.path.exists(wav_path):
                os.remove(wav_path)
            
            return features
            
        except Exception as e:
            logger.error(f"提取音频特征失败: {e}")
            return {}
    
    def split_audio(self, audio_path: str, segment_duration: float = 10.0) -> list:
        """
        分割音频文件
        
        Args:
            audio_path: 音频文件路径
            segment_duration: 每段时长（秒）
        
        Returns:
            分段音频文件路径列表
        """
        try:
            # 加载音频
            audio = AudioSegment.from_file(audio_path)
            duration_ms = len(audio)
            segment_ms = int(segment_duration * 1000)
            
            segments = []
            for i in range(0, duration_ms, segment_ms):
                # 计算分段
                start = i
                end = min(i + segment_ms, duration_ms)
                segment = audio[start:end]
                
                # 保存分段
                segment_path = tempfile.mktemp(suffix='.wav')
                segment.export(segment_path, format='wav')
                segments.append(segment_path)
            
            logger.info(f"音频分割完成: {len(segments)} 段")
            return segments
            
        except Exception as e:
            logger.error(f"音频分割失败: {e}")
            return []
    
    def recognize_sentiment_from_audio(self, audio_path: str) -> dict:
        """
        从音频中识别情感（基础版本）
        
        Args:
            audio_path: 音频文件路径
        
        Returns:
            情感分析结果
        """
        try:
            # 提取音频特征
            features = self.extract_audio_features(audio_path)
            
            if not features:
                return {"sentiment": "neutral", "confidence": 0.5}
            
            # 基于音频特征进行简单的情感判断
            amplitude = features.get("amplitude", {})
            rms = features.get("rms", 0)
            zero_crossing_rate = features.get("zero_crossing_rate", 0)
            
            # 简单的情感判断规则
            if rms > 1000 and zero_crossing_rate > 0.2:
                sentiment = "excited"
                confidence = 0.7
            elif rms < 200 and zero_crossing_rate < 0.1:
                sentiment = "calm"
                confidence = 0.6
            elif amplitude.get("std", 0) > 500:
                sentiment = "angry"
                confidence = 0.65
            else:
                sentiment = "neutral"
                confidence = 0.5
            
            return {
                "sentiment": sentiment,
                "confidence": confidence,
                "features": {
                    "rms": rms,
                    "zero_crossing_rate": zero_crossing_rate,
                    "amplitude_std": amplitude.get("std", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"音频情感识别失败: {e}")
            return {"sentiment": "neutral", "confidence": 0.5}

# 全局音频处理器实例
audio_processor = AudioProcessor()

# 兼容性函数
def speech_to_text(audio_path: str, language: str = "zh-CN") -> str:
    """语音转文本（兼容性函数）"""
    processor = AudioProcessor(language=language)
    return processor.speech_to_text(audio_path)

def text_to_speech(text: str, output_path: str, language: str = "zh-CN") -> Optional[str]:
    """文本转语音（兼容性函数）"""
    processor = AudioProcessor(language=language)
    return processor.text_to_speech(text, output_path)