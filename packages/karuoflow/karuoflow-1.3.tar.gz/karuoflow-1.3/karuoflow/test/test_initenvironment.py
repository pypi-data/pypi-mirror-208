# -*- encoding: utf-8 -*-
'''
@文件    :test_init_environment.py
@说明    :
@时间    :2020/09/02 17:58:36
@作者    :caimmy@hotmail.com
@版本    :0.1
'''
import sys
from pprint import pprint
sys.path.append("/data/work/karuoflow")

import unittest
from karuoflow import InitKaruoflowTables
from karuoflow import DbConfig
from karuoflow.db.session import createDbSession
from karuoflow.initflow import InitializeFlowsFromConfigureWithDbConfig
from karuoflow.error_code import KaruoFlowErrors
from karuoflow.datadef import FlowCustomRuleNode, QueryParams
from karuoflow import KaruoFlow

class InitializeEnvironmentTest(unittest.TestCase):

    def setUp(self):
        self.db = createDbSession(DbConfig('localhost', 'duoneng', 'root', 'Ss2018$Ms0802'))
        self.flow_app = KaruoFlow.CreateModel(session=self.db)

    def test_initenv(self):
        self.assertTrue(InitKaruoflowTables('localhost', 3306, 'duoneng', 'root', 'Ss2018$Ms0802'))

    def test_initflowmodel(self):
        InitializeFlowsFromConfigureWithDbConfig("/home/work/app/duoneng/duoneng/templates/approvalflows/", 'localhost', 3306, 'duoneng', 'root', 'Ss2018$Ms0802')


    def test_queryflow(self):
        m = self.flow_app.QueryFlow("sealapply")
        self.assertTrue(len(m) > 0)

    def test_queryflowlatest(self):
        m = self.flow_app.QueryLastFlow("sealapply")
        self.assertTrue(len(m) > 0)

    def test_applyflow(self):
        _review_def = [
            {"long":{"userid": "long", "dep": "多能电建/彭山公司"}, "abc":{"userid": "abc", "dep": "多能电建/彭山公司"}},
            {"liu": {"userid": "liu", "dep": "多能电建/综合科"}, "li": {"userid": "li", "dep": "多能电建/综合科"}}
        ]
        ret_code, job_id = self.flow_app.Apply("caimmy", "dn_seal", "我要申请盖章", subflow="corp", ext_data={"seal": "**企业法人章"}, rel_prikey=2, 
        reviewer_rule=_review_def)
        self.assertEqual(KaruoFlowErrors.SUCCESS, ret_code)
        self.assertLess(0, job_id)

    def test_applyflow_instance1(self):
        ret_code, job_id = self.flow_app.Apply("sunrui", "dn_confirm_meeting", "test demo")
        print(ret_code)
        print(job_id)

    def test_applylist_indoing(self):
        res = self.flow_app.QueryApplyListInDoing("caimmy", None)
        pprint(res)

    def test_applylist_success(self):
        res = self.flow_app.QueryApplyListSuccessed("caimmy", "sealapply")
        pprint(res)

    def test_review_list(self):
        _checkuser = 'caimmy'
        m = self.flow_app.QueryReviewTodoList(_checkuser)
        for _item in m:
            self.assertTrue(_checkuser in _item["reviewer"])
            self.assertTrue(_item["closed"]=='0')
        pprint(m)

        h = self.flow_app.QueryReviewTodoList("caimmy123", "sealapply")
        self.assertEqual(0, len(h))

    def test_all_flowrules(self):
        m = self.flow_app.QueryAllEnabledFlowRules()
        pprint(m)
        self.assertGreater(len(m), 0)

    def test_recall(self):
        ret_code, job_id = self.flow_app.Apply("recaller", "dn_seal", "我要申请盖章", subflow="person")
        self.assertEqual(KaruoFlowErrors.SUCCESS, ret_code)
        h = self.flow_app.Recall(job_id, "recaller")
        self.assertEqual(KaruoFlowErrors.SUCCESS, h)

    def test_examine(self):
        _review_def = [
            {"long":{"userid": "long", "dep": "多能电建/彭山公司"}, "abc":{"userid": "abc", "dep": "多能电建/彭山公司"}},
            {"liu": {"userid": "liu", "dep": "多能电建/综合科"}, "li": {"userid": "li", "dep": "多能电建/综合科"}}
        ]
        ret_code, job_id = self.flow_app.Apply("caimmy", "dn_seal", "我要申请盖章", subflow="corp", rel_prikey=2, reviewer_rule=_review_def)
        self.assertEqual(KaruoFlowErrors.SUCCESS, ret_code)
        h = self.flow_app.Examine(job_id, "long", True, "同意")
        self.assertEqual(KaruoFlowErrors.SUCCESS, h)
        r = self.flow_app.Examine(job_id, "liu", False, "也是同意不行")
        self.assertEqual(KaruoFlowErrors.SUCCESS, r)

    def test_addsign(self):
        _review_def = [
            {"long":{"userid": "long", "dep": "多能电建/彭山公司"}, "abc":{"userid": "abc", "dep": "多能电建/彭山公司"}},
            {"liu": {"userid": "liu", "dep": "多能电建/综合科"}, "li": {"userid": "li", "dep": "多能电建/综合科"}}
        ]
        ret_code, job_id = self.flow_app.Apply("caimmy", "dn_seal", "我要申请盖章", subflow="corp", rel_prikey=2, reviewer_rule=_review_def)
        self.assertEqual(KaruoFlowErrors.SUCCESS, ret_code)
        query_job_data = self.flow_app.QueryJob(job_id)
        pprint(query_job_data.data["job"]["apply_rules"])
        result = self.flow_app.AddSign(job_id, ["caimmy", "addsign"], "加签", {"asdf": "asdf"}, oper_uid='AndyLau')
        self.assertTrue(result.isSuccess)
        print("----------------------------------------------------")
        query_job_data = self.flow_app.QueryJob(job_id)
        pprint(query_job_data.data["job"]["apply_rules"])

    def test_insertsign(self):
        _review_def = [
            'zhourunfa',
            'guodegang'
        ]
        ret_code, job_id = self.flow_app.Apply("caimmy", "dn_seal", "我要申请盖章", subflow="corp", rel_prikey=2, reviewer_rule=_review_def)
        self.assertEqual(KaruoFlowErrors.SUCCESS, ret_code)
        query_job_data = self.flow_app.QueryJob(job_id)
        pprint(query_job_data.data["job"]["apply_rules"])
        result = self.flow_app.InsertSign(job_id, ["caimmy", "insertsign"], "加签", {"asdf": "asdf"}, oper_uid="JackyChen")
        self.assertTrue(result.isSuccess)
        print("----------------------------------------------------")
        query_job_data = self.flow_app.QueryJob(job_id)
        pprint(query_job_data.data["job"]["apply_rules"])

    def test_examine_mid(self):
        h = self.flow_app.Examine(67, "guofucheng", True, "没问题")
        print(h)

    def test_demo(self):
        m = self.flow_app.QueryReviewTodoList("caimmy", "sealapply")
        if len(m) > 0:
            self.flow_app.Examine(m[0].id, "caimmy", True, "adf")

    def test_query_jobinfor(self):
        t = self.flow_app.QueryJob(443)
        pprint(t.data)

    def test_create_custom_flow(self):
        from karuoflow.datadef import FlowCustomRuleNode
        custom_flows = []
        custom_flows.append(FlowCustomRuleNode(
            "restaurant", 
            reviewer=["long", "guodegang", "liudehua"],
            subflow="15"
        ))

        custom_flows.append(FlowCustomRuleNode(
            "restaurant",
            reviewer=["zhouxingchi", "liangchaowei"]
        ))
        custom_flows.append(FlowCustomRuleNode(
            "restaurant",
            reviewer=["guofucheng", "liming"]
        ))
        ret_code, jobid = self.flow_app.ApplyCustom("caimmy", "restaurant", "asdfjaslfjlasjfasdf", custom_flows, "15", rel_prikey=9527)
        print(ret_code)
        print(jobid)
        self.assertEqual(0, ret_code.value)

    def test_query_my_decided_approvals(self):
        """
        查询自己审核过的申请单
        """
        qp = QueryParams()
        # qp.setContains()
        # qp.setMatches({"catalog": "dn_hold_meeting"})
        tp = QueryParams()
        tp.setContains({"description": "人烦"})
        s = self.flow_app.QueryApplyDecidedByUser("long", agree='1', job_condition=qp, record_condition=tp, page=1, size=100)
        pprint(s)
        # print(len(s.get("sets")))
        # for _item in s.get("sets"):
        #     print(_item["id"])

    def test_launch_approval_v2(self):
        """
        创建第2版审批项
        """
        _review_def = [
            {"long":{"userid": "long", "dep": "多能电建/彭山公司"}, "abc":{"userid": "abc", "dep": "多能电建/彭山公司"}},
            {"liu": {"userid": "liu", "dep": "多能电建/综合科"}, "li": {"userid": "li", "dep": "多能电建/综合科"}}
        ]
        ret_code, job_id = self.flow_app.Apply("caimmy", "caiwu", "申请出差北京2天", subflow="chuchai", ext_data={"dest": "北京大学招待所"}, rel_prikey=2, 
        reviewer_rule=None, version=2)
        self.assertEqual(KaruoFlowErrors.SUCCESS, ret_code)
        self.assertLess(0, job_id)

    def test_launch_approval_custom_v2(self):
        """
        创建第2版自定义审批流程
        """
        _catalog = "caiwu"
        ret_code, job_id = self.flow_app.ApplyCustom("caimmy", _catalog, "custom apply test", [
            FlowCustomRuleNode(_catalog, ['caimmy']),
            FlowCustomRuleNode(_catalog, ['liliqun', 'long'], 'ac', node_label="aaabbb"),
            FlowCustomRuleNode(_catalog, ['caimmy', 'long'], 'chuchai', node_label='middle node', method="joint"),
            FlowCustomRuleNode(_catalog, ['liangchaowei', 'guodegang', "caimmy"], method="joint")
        ], subflow='chuchai')
        self.assertEqual(ret_code, KaruoFlowErrors.SUCCESS)
        print("job_id", job_id)
        self.assertLess(0, job_id)

    def test_coherent_examine(self):
        """
        测试普通审批
        """
        ret_code = self.flow_app.ExamineCoherent(396, "long", True, "demo test")
        print(ret_code)

    def test_examine_stage(self):
        """
        支持会签的审批
        """
        # ret_code = self.flow_app.ExamineStage(445, "caimmy", True, "joint agree", "http://www.baidu.com")
        ret_code = self.flow_app.ExamineStageCoherent(93, "long", True, "joint agree", "http://www.baidu.com")
        print(ret_code)
        print(self.flow_app.QueryJob(434))

    def test_transfer_nextstage(self):
        '''
        测试转移到下一个阶段
        '''
        job_id = 298
        t = self.flow_app.QueryJob(job_id)
        print("-- 1 --")
        pprint(t.data.get("job"))
        res = self.flow_app.TransferNextStage(job_id)
        print("-- 2 --")
        print(res)
        t = self.flow_app.QueryJob(job_id)
        print("-- 3 --")
        pprint(t.data.get("job"))

    def testQueryStageDecisions(self):
        """
        测试阶段审批记录
        """
        t = self.flow_app.QueryJobDecisions(426, 2)
        pprint(t)

    def testSetStageDecisionUsers(self):
        t = self.flow_app.ResetReviewers(456, 1, ['sunwukong', 'zhubajie'])
        pprint(t)


    def testQueryJobByPrikey(self):
        t = self.flow_app.QueryJobViaRelationPrimaryKey("dn_confirm_meeting", 15)
        pprint(t)

        m = self.flow_app.QueryJobViaRelationPrimaryKey("dn_hold_meeting", 28, "office_work")
        pprint(m)

        m = self.flow_app.QueryJobViaRelationPrimaryKey("dn_hold_meeting", 1, "office_work")
        print(m)

    def testAppendFlowNode(self):
        '''
        测试追加签审节点
        '''
        _append_node = [FlowCustomRuleNode("dn_hold_meeting", ["liudehua", "liangchaowei"], "上会申请", "law", "法律专责")]
        _append_node += [FlowCustomRuleNode("dn_hold_meeting", ["haha", "xixi", "hehe"], "上会申请", "dep_leader", "部门会签")]
        _append_node += [FlowCustomRuleNode("dn_hold_meeting", ["xujing", "wangtao"], "上会申请", "corp_leader", "领导会签")]
        result = self.flow_app.AppendSign(173, _append_node)
        pprint(result)

    def testUpdateExtdata(self):
        """
        测试更新扩展数据字段
        """
        _jobid = 5521
        _item = self.flow_app.QueryJob(_jobid)
        if _item.isSuccess:
            _ext_data = _item.data["job"]["ext_data"]
            print(_ext_data)
            if isinstance(_ext_data, dict):
                _ext_data.update({"inuse": 1})
            res = self.flow_app.UpdateJobExtdata(_jobid, _ext_data)
            print(res.toDict)

if "__main__" == __name__:
    unittest.main()