#!/usr/bin/env python3
"""
诗词赏析生成器 - 多线程版本
使用 DeepSeek API 为诗词生成赏析

用法: python3 generate_appreciations.py
"""

import json
import urllib.request
import urllib.error
import threading
import time
import queue
import os
import random
from datetime import datetime

# 从 .env 文件加载环境变量
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())

API_URL = "https://api.chatanywhere.tech/v1/chat/completions"
API_KEY = os.environ.get("OPENAI_API_KEY", "")
CONCURRENCY = 5  # 并发数
BATCH_SAVE = 100   # 每多少条保存一次
REQUEST_TIMEOUT = 60

class PoemGenerator:
    def __init__(self):
        self.poems = []
        self.appreciations = {}
        self.lock = threading.Lock()
        self.success_count = 0
        self.fail_count = 0
        self.progress_lock = threading.Lock()
        self.completed = 0
        self.total = 0
        self.start_time = None
        
    def load_poems(self):
        """加载诗词"""
        with open('data/poems.json', 'r', encoding='utf-8') as f:
            self.poems = json.load(f)
        print(f"已加载 {len(self.poems)} 首诗词")
        
    def load_existing(self):
        """加载已有的赏析"""
        existing_file = 'data/appreciations.json'
        if os.path.exists(existing_file):
            with open(existing_file, 'r', encoding='utf-8') as f:
                self.appreciations = json.load(f)
            print(f"已有 {len(self.appreciations)} 条赏析")
        
    def get_poems_to_generate(self):
        """获取需要生成的诗词列表"""
        need_generate = []
        for poem in self.poems:
            key = poem['title']
            if key not in self.appreciations or not self.appreciations[key].get('appreciation'):
                need_generate.append(poem)
        return need_generate
    
    def generate_prompt(self, poem):
        """生成提示词"""
        title = poem['title']
        author = poem['author']
        dynasty = poem['dynasty']
        content = poem.get('content', [])[:4]
        content_str = '\n'.join(content) if content else '（无诗词内容）'
        
        prompt = f"""为以下诗词写一段赏析：

【诗词】{dynasty}·{author}《{title}》
{content_str}

要求：
1. 赏析60-80字，简洁精炼
2. 突出诗词的艺术特色或情感内涵
3. 格式："赏析内容（来源：出处）"
4. 出处写权威诗集，如《唐诗鉴赏辞典》《宋词鉴赏辞典》《元曲鉴赏辞典》等
5. 仅输出赏析文字，不要其他内容"""

        return prompt
    
    def parse_response(self, text, poem):
        """解析API响应"""
        if not text:
            return None
            
        text = text.strip()
        
        # 提取来源
        source = "来源：网络整理"
        if '（来源：' in text:
            parts = text.rsplit('（来源：', 1)
            if len(parts) == 2:
                text = parts[0].strip()
                source = "来源：" + parts[1].replace('）', '').replace(')', '')
        elif '（来源' in text:
            parts = text.rsplit('（来源', 1)
            if len(parts) == 2:
                text = parts[0].strip()
                source = "来源" + parts[1].replace('）', '').replace(')', '')
        elif '(来源：' in text:
            parts = text.rsplit('(来源：', 1)
            if len(parts) == 2:
                text = parts[0].strip()
                source = "来源：" + parts[1].replace(')', '')
        
        # 确保有括号
        if not text.endswith('）') and not text.endswith(')'):
            text = text + f"（{source}）"
        
        return {
            "appreciation": text,
            "source": source,
            "author": poem['author'],
            "dynasty": poem['dynasty']
        }
    
    def call_api(self, poem, result_queue, tid):
        """调用API"""
        title = poem['title']
        
        prompt = self.generate_prompt(poem)
        
        payload = {
            "model": "deepseek-v4-flash",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 300
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        
        req = urllib.request.Request(
            API_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as response:
                result = json.loads(response.read().decode('utf-8'))
                text = result['choices'][0]['message']['content'].strip()
                parsed = self.parse_response(text, poem)
                result_queue.put((tid, title, parsed, None))
        except Exception as e:
            result_queue.put((tid, title, None, str(e)))
    
    def process_results(self, result_queue, batch_size=BATCH_SAVE):
        """处理结果"""
        while True:
            try:
                tid, title, parsed, err = result_queue.get(timeout=1)
                
                with self.lock:
                    if parsed:
                        self.appreciations[title] = parsed
                        self.success_count += 1
                    else:
                        self.fail_count += 1
                    
                    self.completed += 1
                    
                    # 显示进度
                    elapsed = time.time() - self.start_time
                    speed = self.completed / elapsed if elapsed > 0 else 0
                    remaining = (self.total - self.completed) / speed if speed > 0 else 0
                    
                    print(f"\r进度: {self.completed}/{self.total} ({self.success_count}成功/{self.fail_count}失败) - 速度: {speed:.1f}首/秒 - 预计剩余: {remaining/60:.1f}分钟    ", end='')
                    
                    # 批量保存
                    if self.completed % batch_size == 0:
                        self.save()
                        print(f"\n[自动保存] 已保存 {len(self.appreciations)} 条赏析")
                
                result_queue.task_done()
                
            except queue.Empty:
                if self.completed >= self.total:
                    break
    
    def save(self):
        """保存赏析"""
        with open('data/appreciations.json', 'w', encoding='utf-8') as f:
            json.dump(self.appreciations, f, ensure_ascii=False, indent=2)
    
    def run(self):
        """运行生成器"""
        print("=" * 60)
        print("诗词赏析生成器")
        print("=" * 60)
        
        if not API_KEY:
            print("错误: 未设置 OPENAI_API_KEY 环境变量")
            print("请在 .env 文件中配置: OPENAI_API_KEY=你的API密钥")
            return
        
        self.load_poems()
        self.load_existing()
        
        poems_to_generate = self.get_poems_to_generate()
        self.total = len(poems_to_generate)
        
        if self.total == 0:
            print("\n所有诗词已有赏析！")
            return
        
        # 统计
        tang = sum(1 for p in poems_to_generate if p['dynasty'] == '唐')
        song = sum(1 for p in poems_to_generate if p['dynasty'] == '宋')
        yuan = sum(1 for p in poems_to_generate if p['dynasty'] == '元')
        
        print(f"\n需要生成: {self.total} 首")
        print(f"  - 唐诗: {tang}")
        print(f"  - 宋词: {song}")
        print(f"  - 元曲: {yuan}")
        
        estimated_time = self.total / (CONCURRENCY * 2) / 60  # 估算分钟
        print(f"预计时间: {estimated_time:.0f}-{estimated_time*1.5:.0f} 分钟")
        
        # 自动开始生成
        print("\n自动开始生成...")
        
        print(f"\n开始生成 (并发{CONCURRENCY})...")
        print("-" * 60)
        
        self.start_time = time.time()
        result_queue = queue.Queue()
        
        # 启动结果处理线程
        processor = threading.Thread(target=self.process_results, args=(result_queue,))
        processor.daemon = True
        processor.start()
        
        # 启动工作线程
        threads = []
        poems_added = 0
        
        for i, poem in enumerate(poems_to_generate):
            t = threading.Thread(target=self.call_api, args=(poem, result_queue, i))
            threads.append(t)
            t.start()
            
            # 控制并发
            if len(threads) >= CONCURRENCY:
                for th in threads:
                    th.join()
                threads = []
            
            # 随机延迟避免突发
            if poems_added > 0 and poems_added % 50 == 0:
                time.sleep(random.uniform(0.5, 1.5))
            
            poems_added += 1
        
        # 等待剩余线程
        for t in threads:
            t.join()
        
        # 等待处理完成
        result_queue.join()
        
        # 最终保存
        self.save()
        
        elapsed = time.time() - self.start_time
        
        print("\n")
        print("=" * 60)
        print(f"完成!")
        print(f"  - 成功: {self.success_count} 首")
        print(f"  - 失败: {self.fail_count} 首")
        print(f"  - 总耗时: {elapsed/60:.1f} 分钟")
        print(f"  - 保存至: data/appreciations.json")
        print("=" * 60)
        
        # 显示失败的诗词
        if self.fail_count > 0:
            print(f"\n失败的诗词 ({self.fail_count} 首):")
            # 重新获取失败的
            for poem in poems_to_generate:
                if poem['title'] not in self.appreciations:
                    print(f"  - {poem['dynasty']} {poem['author']}《{poem['title']}》")

if __name__ == "__main__":
    generator = PoemGenerator()
    generator.run()
