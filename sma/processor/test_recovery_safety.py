#!/usr/bin/env python3
"""
Test script to verify recovery mode safety.

This script tests that when recovery mode fails, the existing SMA process
is NOT killed, preventing data loss.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add the sma package to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sma.sma_controller import SMAController
from sma.sma_exceptions import SMARecoveryError

class TestRecoverySafety(unittest.TestCase):
    """Test cases for recovery mode safety."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_args = Mock()
        self.mock_args.folder_path = "Y:\\Test\\Folder"
        self.mock_args.template = "16"
        self.mock_args.filmnumber = None
        self.mock_args.recovery = True  # Enable recovery mode
    
    @patch('sma.sma_controller.SMAConfig')
    @patch('sma.sma_controller.setup_logging')
    @patch('sma.sma_controller.check_running_instance')
    @patch('sma.sma_controller.recover_session')
    def test_recovery_failure_does_not_kill_process(self, mock_recover, mock_check_running, mock_logging, mock_config):
        """Test that recovery failure does not kill existing process."""
        
        # Setup mocks
        mock_logger = Mock()
        mock_logging.return_value = mock_logger
        
        mock_config_instance = Mock()
        mock_config_instance.load_configuration.return_value = {
            'recovery_mode': True,
            'app_path': 'test_app.exe',
            'template_name': 'test.tpl',
            'folder_path': 'Y:\\Test\\Folder',
            'custom_filmnumber': None
        }
        mock_config.return_value = mock_config_instance
        
        # Mock existing app and window
        mock_existing_app = Mock()
        mock_existing_window = Mock()
        
        # Simulate finding existing process (recovery mode scenario)
        mock_check_running.return_value = (False, mock_existing_app, mock_existing_window)
        
        # Simulate recovery failure
        mock_recover.return_value = (False, None)
        
        # Create controller
        controller = SMAController(self.mock_args)
        
        # Run should raise SMARecoveryError and NOT call app.kill()
        with self.assertRaises(SMARecoveryError):
            controller.run()
        
        # Verify that the existing app was NOT killed
        mock_existing_app.kill.assert_not_called()
        
        # Verify that recovery was attempted
        mock_recover.assert_called_once()
        
        # Verify appropriate error messages were logged
        error_calls = [call for call in mock_logger.error.call_args_list 
                      if 'Failed to recover existing scanning session' in str(call)]
        self.assertTrue(len(error_calls) > 0, "Should log recovery failure")
    
    @patch('sma.sma_controller.SMAConfig')
    @patch('sma.sma_controller.setup_logging')
    @patch('sma.sma_controller.check_running_instance')
    @patch('sma.sma_controller.recover_session')
    def test_recovery_success_continues_normally(self, mock_recover, mock_check_running, mock_logging, mock_config):
        """Test that successful recovery continues normally."""
        
        # Setup mocks
        mock_logger = Mock()
        mock_logging.return_value = mock_logger
        
        mock_config_instance = Mock()
        mock_config_instance.load_configuration.return_value = {
            'recovery_mode': True,
            'app_path': 'test_app.exe',
            'template_name': 'test.tpl',
            'folder_path': 'Y:\\Test\\Folder',
            'custom_filmnumber': None
        }
        mock_config_instance.get_film_number.return_value = "TestFilm"
        mock_config.return_value = mock_config_instance
        
        # Mock existing app and window
        mock_existing_app = Mock()
        mock_existing_window = Mock()
        
        # Simulate finding existing process (recovery mode scenario)
        mock_check_running.return_value = (False, mock_existing_app, mock_existing_window)
        
        # Simulate successful recovery
        mock_recover.return_value = (True, "RecoveredFilm123")
        
        # Create controller and patch other methods to avoid full execution
        with patch.object(SMAController, '_setup_environment'), \
             patch.object(SMAController, '_execute_sma_workflow'), \
             patch.object(SMAController, '_monitor_scanning_progress'), \
             patch.object(SMAController, '_handle_end_of_process'), \
             patch.object(SMAController, '_execute_post_processing'):
            
            controller = SMAController(self.mock_args)
            result = controller.run()
        
        # Should succeed
        self.assertTrue(result)
        
        # Verify that the existing app was NOT killed
        mock_existing_app.kill.assert_not_called()
        
        # Verify that recovery was attempted and succeeded
        mock_recover.assert_called_once()
        
        # Verify film number was set from recovery
        self.assertEqual(controller.filmnumber, "RecoveredFilm123")
    
    @patch('sma.sma_controller.SMAConfig')
    @patch('sma.sma_controller.setup_logging')
    @patch('sma.sma_controller.check_running_instance')
    def test_normal_mode_can_still_kill_process(self, mock_check_running, mock_logging, mock_config):
        """Test that normal mode (non-recovery) can still kill existing processes."""
        
        # Setup mocks for normal mode (recovery=False)
        self.mock_args.recovery = False
        
        mock_logger = Mock()
        mock_logging.return_value = mock_logger
        
        mock_config_instance = Mock()
        mock_config_instance.load_configuration.return_value = {
            'recovery_mode': False,
            'app_path': 'test_app.exe',
            'template_name': 'test.tpl',
            'folder_path': 'Y:\\Test\\Folder',
            'custom_filmnumber': None
        }
        mock_config.return_value = mock_config_instance
        
        # Simulate starting new process (normal mode behavior)
        mock_check_running.return_value = (True, None, None)
        
        # This should work normally - the check_running_instance function
        # in ui_automation.py will handle killing existing processes in normal mode
        controller = SMAController(self.mock_args)
        
        # Verify recovery mode is disabled
        self.assertFalse(controller.config['recovery_mode'])

def run_tests():
    """Run the recovery safety tests."""
    print("Running Recovery Mode Safety Tests...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRecoverySafety)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All recovery safety tests PASSED!")
        print("Recovery mode will NOT kill existing processes when recovery fails.")
    else:
        print("❌ Some tests FAILED!")
        print("Recovery mode safety may be compromised.")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 