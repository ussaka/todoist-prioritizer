import unittest
from unittest.mock import patch, Mock
import sys
import os
import configparser

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, src_dir)

from todoist_prioritizer import move_task_to_a_parent


class TestParentProjectFunctionality(unittest.TestCase):
    def setUp(self):
        self.config_patcher = patch("configparser.ConfigParser")
        self.mock_config = self.config_patcher.start()
        self.mock_config_instance = Mock()
        self.mock_config.return_value = self.mock_config_instance
        
        # Mock the configuration to have a parent_id
        self.mock_config_instance.get.side_effect = lambda section, key: "parent123" if key == "parent_id" else "5"

    def tearDown(self):
        self.config_patcher.stop()

    @patch("todoist_prioritizer.api_token")
    def test_parent_project_integration(self, mock_api_token):
        """Test the integration of parent project functionality in the prioritization flow"""
        from todoist_prioritizer import get_tasks, prioritize_tasks
        
        # Mock API responses
        mock_p1_task1 = Mock()
        mock_p1_task1.id = "task1"
        mock_p1_task1.content = "P1 Task 1"
        mock_p1_task1.priority = 4
        mock_p1_task1.due = Mock(date="2023-05-01")
        mock_p1_task1.duration = None

        mock_p1_task2 = Mock()
        mock_p1_task2.id = "task2"
        mock_p1_task2.content = "P1 Task 2"
        mock_p1_task2.priority = 4
        mock_p1_task2.due = Mock(date="2023-05-02")
        mock_p1_task2.duration = Mock(amount=45)

        # Setup mock for filter_tasks
        mock_api_token.filter_tasks.return_value = [[mock_p1_task1, mock_p1_task2]]
        
        # Mock update_task to return success
        mock_api_token.update_task.return_value = {"id": "task1"}
        
        # Test parent project configuration is correctly read
        with patch("todoist_prioritizer.config") as mock_config:
            mock_config.get.return_value = "parent123"
            
            # Call move_task_to_a_parent directly
            move_task_to_a_parent(mock_p1_task1, "parent123")
            
            # Verify API calls
            mock_api_token.update_task.assert_called_with(
                task_id="task1",
                due_string="today at 18:00",
                duration=60,
                duration_unit="minute"
            )
            
            mock_api_token.move_task.assert_called_with(
                task_id="task1",
                project_id="parent123"
            )


if __name__ == "__main__":
    unittest.main()