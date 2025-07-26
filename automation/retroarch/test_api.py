#!/usr/bin/env python3
"""
Test suite for RetroArch HTTP API

Comprehensive tests for all API functionality.
"""

import unittest
import time
import requests
from unittest.mock import patch, MagicMock
from retroarch_api import RetroArchAPI, MultiInstanceAPI, quick_reset, quick_fast_forward

class TestRetroArchAPI(unittest.TestCase):
    def setUp(self):
        """Set up test API instance"""
        self.api = RetroArchAPI(port=55356)
        
    @patch('requests.post')
    def test_send_command_success(self, mock_post):
        """Test successful HTTP command"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'status': 'ok'}
        mock_response.text = '{"status": "ok"}'
        mock_post.return_value = mock_response
        
        result = self.api.send_command('RESET')
        
        mock_post.assert_called_once_with(
            'http://localhost:55356/cmd',
            json={'cmd': 'RESET'},
            timeout=5
        )
        self.assertEqual(result, {'status': 'ok'})
    
    @patch('requests.post')
    def test_send_command_connection_error(self, mock_post):
        """Test HTTP command with connection error"""
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        result = self.api.send_command('RESET')
        
        self.assertEqual(result['status'], 'failed')
        self.assertIn('Connection refused', result['error'])
    
    @patch('socket.socket')
    def test_send_udp_command_success(self, mock_socket):
        """Test successful UDP command"""
        mock_sock = MagicMock()
        mock_socket.return_value = mock_sock
        
        result = self.api.send_udp_command('RESET')
        
        mock_sock.sendto.assert_called_once_with(b'RESET', ('127.0.0.1', 55356))
        mock_sock.close.assert_called_once()
        self.assertEqual(result, {'status': 'sent'})
    
    @patch('socket.socket')
    def test_send_udp_command_error(self, mock_socket):
        """Test UDP command with error"""
        mock_socket.side_effect = Exception("UDP error")
        
        result = self.api.send_udp_command('RESET')
        
        self.assertEqual(result['status'], 'failed')
        self.assertIn('UDP error', result['error'])
    
    @patch.object(RetroArchAPI, 'send_command')
    def test_reset_game(self, mock_send):
        """Test game reset command"""
        mock_send.return_value = {'status': 'ok'}
        
        result = self.api.reset_game()
        
        mock_send.assert_called_once_with('RESET')
        self.assertEqual(result, {'status': 'ok'})
    
    @patch.object(RetroArchAPI, 'send_command')
    def test_fast_forward(self, mock_send):
        """Test fast forward command"""
        mock_send.return_value = {'status': 'ok'}
        
        result = self.api.fast_forward()
        
        mock_send.assert_called_once_with('FAST_FORWARD')
        self.assertEqual(result, {'status': 'ok'})
    
    @patch.object(RetroArchAPI, 'send_command')
    def test_pause_toggle(self, mock_send):
        """Test pause toggle command"""
        mock_send.return_value = {'status': 'ok'}
        
        result = self.api.pause_toggle()
        
        mock_send.assert_called_once_with('PAUSE_TOGGLE')
        self.assertEqual(result, {'status': 'ok'})
    
    @patch.object(RetroArchAPI, 'send_command')
    def test_save_state(self, mock_send):
        """Test save state command"""
        mock_send.return_value = {'status': 'ok'}
        
        result = self.api.save_state(slot=3)
        
        mock_send.assert_called_once_with('SAVE_STATE_SLOT 3')
        self.assertEqual(result, {'status': 'ok'})
    
    @patch.object(RetroArchAPI, 'send_command')
    def test_load_state(self, mock_send):
        """Test load state command"""
        mock_send.return_value = {'status': 'ok'}
        
        result = self.api.load_state(slot=5)
        
        mock_send.assert_called_once_with('LOAD_STATE_SLOT 5')
        self.assertEqual(result, {'status': 'ok'})
    
    @patch.object(RetroArchAPI, 'send_command')
    def test_screenshot(self, mock_send):
        """Test screenshot command"""
        mock_send.return_value = {'status': 'ok'}
        
        result = self.api.screenshot()
        
        mock_send.assert_called_once_with('SCREENSHOT')
        self.assertEqual(result, {'status': 'ok'})
    
    @patch.object(RetroArchAPI, 'send_command')
    def test_quit(self, mock_send):
        """Test quit command"""
        mock_send.return_value = {'status': 'ok'}
        
        result = self.api.quit()
        
        mock_send.assert_called_once_with('QUIT')
        self.assertEqual(result, {'status': 'ok'})

class TestMultiInstanceAPI(unittest.TestCase):
    def setUp(self):
        """Set up test multi-instance API"""
        self.multi_api = MultiInstanceAPI(num_instances=3, port_base=55355)
    
    def test_initialization(self):
        """Test multi-instance API initialization"""
        self.assertEqual(len(self.multi_api.instances), 3)
        self.assertIsInstance(self.multi_api.instances[1], RetroArchAPI)
        self.assertEqual(self.multi_api.instances[1].port, 55356)
        self.assertEqual(self.multi_api.instances[3].port, 55358)
    
    def test_get_instance(self):
        """Test getting specific instance"""
        instance = self.multi_api.get_instance(2)
        self.assertIsInstance(instance, RetroArchAPI)
        self.assertEqual(instance.port, 55357)
        
        # Test invalid instance
        invalid = self.multi_api.get_instance(99)
        self.assertIsNone(invalid)
    
    @patch.object(RetroArchAPI, 'reset_game')
    def test_reset_all(self, mock_reset):
        """Test reset all instances"""
        mock_reset.return_value = {'status': 'ok'}
        
        results = self.multi_api.reset_all()
        
        self.assertEqual(len(results), 3)
        self.assertEqual(mock_reset.call_count, 3)
        for i in range(1, 4):
            self.assertEqual(results[i], {'status': 'ok'})
    
    @patch.object(RetroArchAPI, 'fast_forward')
    def test_fast_forward_all(self, mock_ff):
        """Test fast forward all instances"""
        mock_ff.return_value = {'status': 'ok'}
        
        results = self.multi_api.fast_forward_all()
        
        self.assertEqual(len(results), 3)
        self.assertEqual(mock_ff.call_count, 3)
        for i in range(1, 4):
            self.assertEqual(results[i], {'status': 'ok'})
    
    @patch.object(RetroArchAPI, 'screenshot')
    def test_screenshot_all(self, mock_screenshot):
        """Test screenshot all instances"""
        mock_screenshot.return_value = {'status': 'ok'}
        
        results = self.multi_api.screenshot_all()
        
        self.assertEqual(len(results), 3)
        self.assertEqual(mock_screenshot.call_count, 3)
        for i in range(1, 4):
            self.assertEqual(results[i], {'status': 'ok'})
    
    @patch.object(RetroArchAPI, 'send_command')
    def test_command_all(self, mock_send):
        """Test sending command to all instances"""
        mock_send.return_value = {'status': 'ok'}
        
        results = self.multi_api.command_all('PAUSE_TOGGLE')
        
        self.assertEqual(len(results), 3)
        self.assertEqual(mock_send.call_count, 3)
        for call in mock_send.call_args_list:
            self.assertEqual(call[0][0], 'PAUSE_TOGGLE')

class TestConvenienceFunctions(unittest.TestCase):
    @patch('retroarch_api.RetroArchAPI')
    def test_quick_reset(self, mock_api_class):
        """Test quick reset convenience function"""
        mock_api = MagicMock()
        mock_api.reset_game.return_value = {'status': 'ok'}
        mock_api_class.return_value = mock_api
        
        result = quick_reset(instance_id=2, port_base=55355)
        
        mock_api_class.assert_called_once_with(55357)  # 55355 + 2
        mock_api.reset_game.assert_called_once()
        self.assertEqual(result, {'status': 'ok'})
    
    @patch('retroarch_api.RetroArchAPI')
    def test_quick_fast_forward(self, mock_api_class):
        """Test quick fast forward convenience function"""
        mock_api = MagicMock()
        mock_api.fast_forward.return_value = {'status': 'ok'}
        mock_api_class.return_value = mock_api
        
        result = quick_fast_forward(instance_id=1, port_base=55355)
        
        mock_api_class.assert_called_once_with(55356)  # 55355 + 1
        mock_api.fast_forward.assert_called_once()
        self.assertEqual(result, {'status': 'ok'})

class TestIntegration(unittest.TestCase):
    """Integration tests that can run against real RetroArch instances"""
    
    def setUp(self):
        """Set up for integration tests"""
        self.api = RetroArchAPI(port=55356)
        
    def test_http_connection_refused(self):
        """Test behavior when RetroArch is not running"""
        # This test assumes RetroArch is NOT running on port 55356
        result = self.api.reset_game()
        
        self.assertEqual(result['status'], 'failed')
        self.assertIn('error', result)
    
    def test_udp_command_no_response(self):
        """Test UDP command when RetroArch is not running"""
        # UDP doesn't give connection errors, just sends
        result = self.api.send_udp_command('RESET')
        
        self.assertEqual(result['status'], 'sent')

def run_live_tests():
    """Run tests against actual RetroArch instances (if running)"""
    print("🧪 Running Live RetroArch API Tests")
    print("=" * 40)
    
    # Test different ports to find running instances
    ports_to_test = [55356, 55357, 55358]
    
    for port in ports_to_test:
        print(f"\n🔌 Testing port {port}...")
        api = RetroArchAPI(port)
        
        # Try HTTP first
        print("  HTTP commands:")
        result = api.send_command('PAUSE_TOGGLE')
        print(f"    PAUSE_TOGGLE: {result}")
        
        result = api.send_command('PAUSE_TOGGLE')  # Toggle back
        print(f"    PAUSE_TOGGLE (back): {result}")
        
        # Try UDP
        print("  UDP commands:")
        result = api.send_udp_command('FAST_FORWARD')
        print(f"    FAST_FORWARD: {result}")
        
        time.sleep(0.5)  # Brief pause between tests

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--live':
        # Run live tests against actual RetroArch
        run_live_tests()
    else:
        # Run unit tests
        print("🧪 Running RetroArch API Unit Tests")
        print("=" * 40)
        unittest.main(verbosity=2) 