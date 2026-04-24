#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
造梦.skill - 主入口点
提供 CLI 界面，处理命令行参数，分发到相应模块
"""

import argparse
import sys
import os
import time
from pathlib import Path

# 添加 src 目录到 Python 路径
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from src.core.config import Config
from src.modules.distillation import NovelDistiller
from src.modules.chat_engine import ChatEngine
from src.modules.relationships import RelationshipExtractor


class DreamForgeCLI:
    """造梦.skill 命令行接口"""
    
    def __init__(self):
        self.config = Config()
        self.parser = self._create_parser()
        
    def _create_parser(self):
        """创建命令行参数解析器"""
        parser = argparse.ArgumentParser(
            description="造梦.skill - 小说角色心智蒸馏与模拟工具",
            epilog="详细信息请参考 PROJECT.md"
        )
        subparsers = parser.add_subparsers(dest="command", help="可用命令")
        
        # distill 命令：小说蒸馏
        distill_parser = subparsers.add_parser("distill", help="从小说文本中蒸馏角色心智")
        distill_parser.add_argument("--novel", "-n", required=True, 
                                  help="小说文件路径 (.txt 或 .epub)")
        distill_parser.add_argument("--characters", "-c", 
                                  help="指定角色列表，逗号分隔 (如：林黛玉,贾宝玉)")
        distill_parser.add_argument("--output", "-o", 
                                  help="输出目录，默认为 data/characters/")
        distill_parser.add_argument("--force", "-f", action="store_true",
                                  help="跳过费用确认，直接执行")
        
        # chat 命令：角色群聊
        chat_parser = subparsers.add_parser("chat", help="启动角色群聊会话")
        chat_parser.add_argument("--novel", "-n", required=True,
                               help="小说名称或角色档案目录")
        chat_parser.add_argument("--mode", "-m", choices=["observe", "act"], 
                               default="observe",
                               help="交互模式：observe(旁观) 或 act(代入)")
        chat_parser.add_argument("--character", "-c",
                               help="代入模式时指定角色名")
        chat_parser.add_argument("--session", "-s",
                               help="会话 ID，用于恢复之前会话")
        
        # view 命令：查看角色档案
        view_parser = subparsers.add_parser("view", help="查看角色心智档案")
        view_parser.add_argument("--character", "-c", required=True,
                               help="角色名")
        
        # correct 命令：纠正 OOC 行为
        correct_parser = subparsers.add_parser("correct", help="纠正角色 OOC 行为")
        correct_parser.add_argument("--session", "-s", required=True,
                                  help="会话 ID")
        correct_parser.add_argument("--message", "-m", required=True,
                                  help="需要纠正的原句")
        correct_parser.add_argument("--corrected", "-c", required=True,
                                  help="纠正后的句子")
        correct_parser.add_argument("--character", "-r",
                                  help="角色名")
        correct_parser.add_argument("--target", "-t",
                                  help="对象角色名")
        correct_parser.add_argument("--reason",
                                  help="纠错原因")
        
        # extract 命令：提取关系
        extract_parser = subparsers.add_parser("extract", help="从小说中提取角色关系")
        extract_parser.add_argument("--novel", "-n", required=True,
                                  help="小说文件路径")
        extract_parser.add_argument("--output", "-o",
                                  help="输出文件路径")
        extract_parser.add_argument("--force", "-f", action="store_true",
                                  help="跳过费用确认，直接执行")
        
        return parser
    
    def run(self):
        """运行 CLI"""
        args = self.parser.parse_args()
        
        if not args.command:
            self.parser.print_help()
            return
        
        try:
            if args.command == "distill":
                self._handle_distill(args)
            elif args.command == "chat":
                self._handle_chat(args)
            elif args.command == "view":
                self._handle_view(args)
            elif args.command == "correct":
                self._handle_correct(args)
            elif args.command == "extract":
                self._handle_extract(args)
            else:
                print(f"未知命令: {args.command}")
                sys.exit(1)
                
        except KeyboardInterrupt:
            print("\n\n操作已取消")
            sys.exit(0)
        except Exception as e:
            print(f"错误: {e}")
            sys.exit(1)
    
    def _handle_distill(self, args):
        """处理蒸馏命令"""
        print("=== 小说人物心智蒸馏 ===")
        
        # 初始化蒸馏器
        distiller = NovelDistiller(self.config)
        
        # 确认费用
        if not args.force:
            cost_estimate = distiller.estimate_cost(args.novel)
            print(f"预估费用: ${cost_estimate:.2f} USD")
            confirm = input("确认执行？ (y/n): ").strip().lower()
            if confirm != "y":
                print("操作已取消")
                return
        
        # 执行蒸馏
        characters = args.characters.split(",") if args.characters else None
        output_dir = args.output or self.config.get_path("characters")
        
        print(f"开始处理小说: {args.novel}")
        result = distiller.distill(args.novel, characters, output_dir)
        
        print(f"\n完成！共提取 {len(result)} 个角色")
        for char_name in result:
            print(f"  - {char_name}")
    
    def _handle_chat(self, args):
        """处理聊天命令"""
        print("=== 角色群聊引擎 ===")
        
        # 初始化聊天引擎
        engine = ChatEngine(self.config)
        
        if args.session:
            # 恢复会话
            session = engine.restore_session(args.session)
            print(f"恢复会话: {session['title']}")
        else:
            # 新会话
            characters_dir = self.config.get_path("characters")
            if not os.path.exists(characters_dir):
                print(f"错误: 角色档案目录不存在: {characters_dir}")
                print("请先运行 'distill' 命令提取角色")
                return
            
            print(f"加载角色档案: {args.novel}")
            session = engine.create_session(args.novel, args.mode)
        
        # 运行聊天
        if args.mode == "act" and args.character:
            engine.act_mode(session, args.character)
        else:
            engine.observe_mode(session)
    
    def _handle_view(self, args):
        """处理查看命令"""
        import json
        
        char_path = os.path.join(self.config.get_path("characters"), 
                                f"{args.character}.json")
        
        if not os.path.exists(char_path):
            print(f"错误: 角色档案不存在: {args.character}")
            return
        
        with open(char_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"=== {args.character} 角色档案 ===")
        print(f"核心特质: {', '.join(data.get('core_traits', []))}")
        print(f"语言风格: {data.get('speech_style', '')}")
        print("\n价值观维度:")
        for dim, value in data.get('values', {}).items():
            print(f"  {dim}: {value}/10")
        
        if 'typical_lines' in data:
            print(f"\n经典台词:")
            for line in data['typical_lines'][:5]:
                print(f"  - {line}")
    
    def _handle_correct(self, args):
        """处理纠正命令"""
        print("=== 纠正 OOC 行为 ===")
        
        # 保存纠正记录
        corrections_dir = self.config.get_path("corrections")
        os.makedirs(corrections_dir, exist_ok=True)
        
        correction = {
            "session_id": args.session,
            "character": args.character or "unknown",
            "target": args.target or "",
            "original_message": args.message,
            "corrected_message": args.corrected,
            "reason": args.reason or "",
            "timestamp": time.time()
        }
        
        # 保存到文件
        import json
        filename = f"correction_{args.session}_{int(time.time())}.json"
        filepath = os.path.join(corrections_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(correction, f, ensure_ascii=False, indent=2)
        
        print(f"纠正已保存: {filepath}")
    
    def _handle_extract(self, args):
        """处理关系提取命令"""
        print("=== 角色关系提取 ===")
        
        extractor = RelationshipExtractor(self.config)
        
        if not args.force:
            cost_estimate = extractor.estimate_cost(args.novel)
            print(f"预估费用: ${cost_estimate:.2f} USD")
            confirm = input("确认执行？ (y/n): ").strip().lower()
            if confirm != "y":
                print("操作已取消")
                return
        
        output_path = args.output or self.config.get_path("relations")
        result = extractor.extract(args.novel, output_path)
        
        print(f"\n完成！共提取 {len(result)} 对角色关系")
        for rel_key in list(result.keys())[:5]:
            print(f"  - {rel_key}")


def main():
    """主函数"""
    cli = DreamForgeCLI()
    cli.run()


if __name__ == "__main__":
    main()
