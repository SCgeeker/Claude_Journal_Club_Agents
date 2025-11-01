#!/usr/bin/env python3
"""
端到端測試：Knowledge Base Manager Agent
測試3個核心工作流
"""
import sys
from datetime import datetime

# 導入Agent（Agent內部會處理UTF-8編碼）
from src.agents import KnowledgeBaseManagerAgent


def test_agent_initialization():
    """測試1：Agent初始化"""
    print("=" * 70)
    print("測試1：Agent初始化")
    print("=" * 70)

    try:
        agent = KnowledgeBaseManagerAgent()
        print(f"✅ Agent初始化成功")
        print(f"   可用工作流: {len(agent.workflows)} 個")
        print(f"   可用Skills: {len(agent.skills)} 個\n")
        return agent, True
    except Exception as e:
        print(f"❌ Agent初始化失敗: {e}")
        return None, False


def test_workflow_integrate_zettel(agent):
    """測試2：整合Zettelkasten工作流"""
    print("\n" + "=" * 70)
    print("測試2：整合Zettelkasten工作流")
    print("=" * 70)

    try:
        # 執行工作流（使用已索引的資料，應該跳過）
        result = agent.integrate_zettel(
            zettel_dir="output/zettelkasten_notes",
            domain="all",
            auto_link=True,
            similarity_threshold=0.7
        )

        if result.get('success'):
            print(f"✅ 工作流執行成功")
            print(f"   總卡片數: {result.get('total_cards', 0)}")
            print(f"   成功索引: {result.get('success', 0)}")
            print(f"   跳過: {result.get('skipped', 0)}")

            if 'linking' in result:
                link_stats = result['linking']
                print(f"   論文關聯: {link_stats.get('linked', 0)} 個")

            return True
        else:
            print(f"❌ 工作流執行失敗: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_workflow_quality_audit(agent):
    """測試3：質量審計工作流"""
    print("\n" + "=" * 70)
    print("測試3：質量審計工作流")
    print("=" * 70)

    try:
        result = agent.quality_audit(
            severity="all",
            auto_fix=False,
            detect_duplicates=True
        )

        if result.get('success'):
            print(f"✅ 工作流執行成功")
            print(f"   發現問題: {result.get('issues_found', 0)} 個")
            print(f"   重複論文: {result.get('duplicates', 0)} 個")
            return True
        else:
            print(f"❌ 工作流執行失敗: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_workflow_search(agent):
    """測試4：搜索功能（額外測試）"""
    print("\n" + "=" * 70)
    print("測試4：搜索功能")
    print("=" * 70)

    try:
        kb = agent.skills['kb-connector']

        # 測試搜索Zettelkasten
        results = kb.search_zettel("mass noun", limit=5)

        print(f"✅ 搜索成功")
        print(f"   找到 {len(results)} 個結果")

        if results:
            print(f"\n   前3個結果:")
            for i, card in enumerate(results[:3], 1):
                print(f"     {i}. [{card['zettel_id']}] {card['title'][:50]}")
                print(f"        領域: {card['domain']}, 類型: {card['card_type']}")

        return len(results) > 0

    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_skill_dispatch(agent):
    """測試5：Skill調度功能"""
    print("\n" + "=" * 70)
    print("測試5：Skill調度功能")
    print("=" * 70)

    try:
        # 測試各個Skill是否可用
        skills_status = {}

        for skill_name, skill_instance in agent.skills.items():
            try:
                # 簡單檢查Skill實例是否正常
                if skill_instance is not None:
                    skills_status[skill_name] = "✅ 可用"
                else:
                    skills_status[skill_name] = "❌ 未初始化"
            except Exception as e:
                skills_status[skill_name] = f"❌ 錯誤: {e}"

        print("Skill狀態:")
        for skill, status in skills_status.items():
            print(f"  {skill}: {status}")

        all_available = all("✅" in status for status in skills_status.values())

        if all_available:
            print(f"\n✅ 所有Skill可用")
            return True
        else:
            print(f"\n⚠️  部分Skill不可用")
            return False

    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False


def generate_test_report(test_results: dict):
    """生成測試報告"""
    print("\n" + "=" * 70)
    print("📊 端到端測試報告")
    print("=" * 70)

    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    print(f"\n⏱️  測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n📈 總結:")
    print(f"   - 總測試數: {total_tests}")
    print(f"   - 通過: {passed_tests}")
    print(f"   - 失敗: {total_tests - passed_tests}")
    print(f"   - 成功率: {success_rate:.1f}%")

    print(f"\n📋 測試詳情:")
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")

    print(f"\n{'='*70}")

    if success_rate == 100:
        print("🎉 所有測試通過！Agent系統可用。")
    elif success_rate >= 80:
        print("⚠️  大部分測試通過，但有部分問題需要處理。")
    else:
        print("❌ 測試未通過，Agent系統可能存在問題。")

    print("=" * 70)

    return success_rate


def main():
    """主測試流程"""
    print("\n🧪 Knowledge Base Manager Agent - 端到端測試")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    test_results = {}

    # 測試1：初始化
    agent, init_success = test_agent_initialization()
    test_results["1. Agent初始化"] = init_success

    if not init_success:
        print("\n❌ Agent初始化失敗，無法繼續測試")
        return

    # 測試2：整合Zettelkasten
    test_results["2. 整合Zettelkasten"] = test_workflow_integrate_zettel(agent)

    # 測試3：質量審計
    test_results["3. 質量審計"] = test_workflow_quality_audit(agent)

    # 測試4：搜索功能
    test_results["4. 搜索功能"] = test_workflow_search(agent)

    # 測試5：Skill調度
    test_results["5. Skill調度"] = test_skill_dispatch(agent)

    # 生成報告
    success_rate = generate_test_report(test_results)

    # 保存報告
    report_file = f"AGENT_E2E_TEST_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"Agent端到端測試報告\n")
        f.write(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"成功率: {success_rate:.1f}%\n\n")
        for test_name, result in test_results.items():
            status = "PASS" if result else "FAIL"
            f.write(f"{test_name}: {status}\n")

    print(f"\n💾 報告已保存: {report_file}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  測試被用戶中斷")
    except Exception as e:
        print(f"\n\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
