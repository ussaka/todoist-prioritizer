import unittest
from unittest.mock import patch
import sys
import os
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, src_dir)

from todoist_prioritizer import check_for_updates
from todoist_prioritizer import current_version
from todoist_prioritizer import get_tasks
from todoist_prioritizer import sort_tasks_date
from todoist_prioritizer import convert_priority
from todoist_prioritizer import prioritize_tasks, fill_today_tasks


class Task:
    def __init__(self, id, content, created_at, priority):
        self.id = id
        self.content = content
        self.created_at = created_at
        self.priority = priority


mock_tasks = [
    Task(
        id="2995104339",
        content="data1",
        created_at="2021-12-11T22:36:50.000000Z",
        priority=4,
    ),
    Task(
        id="2995104340",
        content="data2",
        created_at="2019-10-02T15:15:42.000000Z",
        priority=3,
    ),
    Task(
        id="2995104341",
        content="data3",
        created_at="2024-06-05T15:44:59.000000Z",
        priority=2,
    ),
    Task(
        id="2995104342",
        content="data4",
        created_at="2022-01-01T12:00:00.000000Z",
        priority=1,
    ),
    Task(
        id="2995104343",
        content="data5",
        created_at="2022-01-01T12:00:00.000000Z",
        priority=4,
    ),
    Task(
        id="2995104344",
        content="data6",
        created_at="2022-01-01T12:00:00.000000Z",
        priority=3,
    ),
    Task(
        id="2995104345",
        content="data7",
        created_at="2022-01-01T12:00:00.000000Z",
        priority=2,
    ),
    Task(
        id="2995104346",
        content="data8",
        created_at="2022-01-01T12:00:00.000000Z",
        priority=1,
    ),
    Task(
        id="2995104347",
        content="data9",
        created_at="2022-01-01T12:00:00.000000Z",
        priority=1,
    ),
    Task(
        id="2995104348",
        content="data10",
        created_at="2022-01-01T12:00:00.000000Z",
        priority=2,
    ),
    Task(
        id="2995104349",
        content="data11",
        created_at="2022-01-01T12:00:00.000000Z",
        priority=3,
    ),
    Task(
        id="2995104350",
        content="data12",
        created_at="2022-01-01T12:00:00.000000Z",
        priority=4,
    ),
    Task(
        id="2995104351",
        content="data13",
        created_at="2022-01-01T12:00:00.000000Z",
        priority=4,
    ),
    Task(
        id="2995104352",
        content="data14",
        created_at="2022-01-01T12:00:00.000000Z",
        priority=0,
    ),
    Task(
        id="2995104353",
        content="data15",
        created_at="2022-01-01T12:00:00.000000Z",
        priority=5,
    ),
    Task(
        id="2995104354",
        content="data16",
        created_at="2022-01-01T12:00:00.000000Z",
        priority=6,
    ),
    Task(
        id="2995104355",
        content="data17",
        created_at="2022-01-01T12:00:00.000000Z",
        priority=1,
    ),
    # Task with empty content
    Task(
        id="2995104356",
        content="",
        created_at="2022-01-01T12:00:00.000000Z",
        priority=3,
    ),
    # Task with future creation date
    Task(
        id="2995104357",
        content="data18",
        created_at="2999-01-01T12:00:00.000000Z",
        priority=2,
    ),
    # Task with past creation date
    Task(
        id="2995104358",
        content="data19",
        created_at="1990-01-01T12:00:00.000000Z",
        priority=1,
    ),
    # Task with invalid creation date format
    Task(
        id="2995104359",
        content="data20",
        created_at="2022-01-01",
        priority=4,
    ),
]


class TodoistPrioritizerHelperFunctionsTest(unittest.TestCase):
    def setUp(self):
        self.tasks = mock_tasks

    def test_check_for_updates(self):
        response = check_for_updates()
        self.assertEqual(response.status_code, 200)

        releases = response.json()
        latest_release = releases[0]["tag_name"]
        self.assertEqual(latest_release, current_version)

    def test_check_for_updates_invalid(self):
        """Test check_for_updates when the API call fails."""
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 500
            response = check_for_updates()
            self.assertEqual(response.status_code, 500)

    def test_get_tasks(self):
        """Test get_tasks returns only tasks with the desired priority."""
        desired_priority = 4
        expected_tasks = [
            task for task in self.tasks if task.priority == desired_priority
        ]

        with patch("todoist_prioritizer.api_token") as mock_api_token:
            mock_api_token.get_tasks.return_value = expected_tasks
            tasks = get_tasks("P1")
            self.assertTrue(all(task.priority == desired_priority for task in tasks))
            self.assertEqual(tasks, expected_tasks)
            mock_api_token.get_tasks.assert_called_with(filter="P1")

    def test_sort_tasks_date(self):
        sorted_tasks = sort_tasks_date(self.tasks)
        self.assertEqual(sorted_tasks, sorted(self.tasks, key=lambda x: x.created_at))

    def test_convert_priority(self):
        self.assertEqual(convert_priority(1), 4)
        self.assertEqual(convert_priority(2), 3)
        self.assertEqual(convert_priority(3), 2)
        self.assertEqual(convert_priority(4), 1)

    def test_convert_priority_invalid(self):
        """Test converting an invalid priority."""
        with self.assertRaises(ValueError):
            convert_priority(0)
        with self.assertRaises(ValueError):
            convert_priority(5)

    def test_prioritize_tasks(self):
        """Test prioritizing tasks with valid inputs and filtered mock."""
        desired_priority = 4
        max_size = 3

        def mock_get_tasks(filter=None):
            # Simulate Todoist API filter: "P1" means priority 4, etc.
            if filter == "P1":
                return [task for task in self.tasks if task.priority == 4][:max_size]
            elif filter == "P2":
                return [task for task in self.tasks if task.priority == 3][:max_size]
            elif filter == "P3":
                return [task for task in self.tasks if task.priority == 2][:max_size]
            elif filter == "P4":
                return [task for task in self.tasks if task.priority == 1][:max_size]
            return []

        with patch("todoist_prioritizer.api_token") as mock_api_token:
            mock_api_token.update_task.return_value = {"content": "mocked_task"}
            filtered_tasks = mock_get_tasks("P1")
            prioritized_tasks = prioritize_tasks(
                filtered_tasks, desired_priority, max_size
            )
            self.assertEqual(len(prioritized_tasks), len(filtered_tasks))
            self.assertTrue(
                all(task.priority == desired_priority for task in prioritized_tasks)
            )
            mock_api_token.update_task.assert_called()


if __name__ == "__main__":
    unittest.main()
