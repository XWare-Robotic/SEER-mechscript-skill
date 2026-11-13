"""用假时钟和设备替身验证动作的逐帧推进。"""

import unittest
from enum import Enum
from typing import NamedTuple, Optional


class StepStatus(Enum):
    READY = "待下发"
    RUNNING = "等待反馈"
    FINISHED = "到位"
    FAILED = "失败"
    CANCELLED = "取消"


class Feedback(NamedTuple):
    request_id: int
    accepted: Optional[bool]
    reached: Optional[bool]


class ActionStep:
    """每帧发送一次请求或检查一次反馈。"""

    def __init__(self, device, clock, timeout_s):
        self.device = device
        self.clock = clock
        self.timeout_s = timeout_s
        self.status = StepStatus.READY
        self.failure_reason = None
        self.request_id = None
        self.deadline_s = None

    def tick(self):
        if self.status is StepStatus.READY:
            self.deadline_s = self.clock() + self.timeout_s
            self.request_id = self.device.send()
            self.status = StepStatus.RUNNING
            return self.status
        if self.status is not StepStatus.RUNNING:
            return self.status
        if self.clock() >= self.deadline_s:
            self.status = StepStatus.FAILED
            self.failure_reason = "等待到位超时"
            return self.status

        feedback = self.device.read_feedback()
        if feedback is None or feedback.request_id != self.request_id:
            return self.status
        if feedback.accepted is False:
            self.status = StepStatus.FAILED
            self.failure_reason = "设备拒绝请求"
        elif feedback.accepted is True and feedback.reached is True:
            self.status = StepStatus.FINISHED
        return self.status

    def cancel(self):
        if self.status is StepStatus.RUNNING:
            self.device.request_cancel(self.request_id)
        if self.status in (StepStatus.READY, StepStatus.RUNNING):
            self.status = StepStatus.CANCELLED
        return self.status


class FakeClock:
    def __init__(self):
        self.now_s = 0.0

    def __call__(self):
        return self.now_s


class FakeDevice:
    def __init__(self, feedback):
        self.feedback = iter(feedback)
        self.calls = []

    def send(self):
        self.calls.append("send")
        return 7

    def read_feedback(self):
        self.calls.append("read_feedback")
        return next(self.feedback, None)

    def request_cancel(self, request_id):
        self.calls.append(("request_cancel", request_id))


class ReplayTests(unittest.TestCase):
    def make_step(self, *feedback):
        self.clock = FakeClock()
        self.device = FakeDevice(feedback)
        return ActionStep(self.device, self.clock, timeout_s=5.0)

    def test_send_then_wait_for_position(self):
        step = self.make_step(Feedback(7, True, False), Feedback(7, True, True))
        self.assertIs(step.tick(), StepStatus.RUNNING)
        self.assertEqual(self.device.calls, ["send"])
        self.assertIs(step.tick(), StepStatus.RUNNING)
        self.assertIs(step.tick(), StepStatus.FINISHED)
        self.assertIs(step.tick(), StepStatus.FINISHED)
        self.assertEqual(self.device.calls, ["send", "read_feedback", "read_feedback"])

    def test_missing_or_unmatched_feedback(self):
        step = self.make_step(
            None, Feedback(6, True, True), Feedback(7, True, None), Feedback(7, None, True)
        )
        for _ in range(5):
            self.assertIs(step.tick(), StepStatus.RUNNING)
        self.assertEqual(self.device.calls.count("send"), 1)

    def test_timeout(self):
        step = self.make_step(Feedback(7, True, True))
        self.assertIs(step.tick(), StepStatus.RUNNING)
        self.clock.now_s = 5.0
        self.assertIs(step.tick(), StepStatus.FAILED)
        self.assertEqual(step.failure_reason, "等待到位超时")
        self.assertIs(step.tick(), StepStatus.FAILED)
        self.assertEqual(self.device.calls, ["send"])

    def test_rejection(self):
        step = self.make_step(Feedback(7, False, None))
        self.assertIs(step.tick(), StepStatus.RUNNING)
        self.assertIs(step.tick(), StepStatus.FAILED)
        self.assertEqual(step.failure_reason, "设备拒绝请求")

    def test_cancel(self):
        step = self.make_step(Feedback(7, True, True))
        self.assertIs(step.tick(), StepStatus.RUNNING)
        self.assertIs(step.cancel(), StepStatus.CANCELLED)
        self.assertIs(step.cancel(), StepStatus.CANCELLED)
        self.assertIs(step.tick(), StepStatus.CANCELLED)
        self.assertEqual(self.device.calls, ["send", ("request_cancel", 7)])


if __name__ == "__main__":
    unittest.main()
