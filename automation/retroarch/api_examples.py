#!/usr/bin/env python3
"""
RetroArch HTTP API Usage Examples

Practical examples for Pokemon automation scenarios.
"""

import time
from retroarch_api import RetroArchAPI, MultiInstanceAPI, quick_reset, quick_fast_forward

def example_single_instance():
    """Example: Control a single RetroArch instance"""
    print("🎮 Single Instance Control Example")
    print("-" * 40)
    
    # Connect to instance 1 (port 55356)
    api = RetroArchAPI(port=55356)
    
    print("1. Enabling fast forward...")
    result = api.fast_forward()
    print(f"   Result: {result}")
    
    print("2. Resetting game...")
    result = api.reset_game()
    print(f"   Result: {result}")
    
    print("3. Taking screenshot...")
    result = api.screenshot()
    print(f"   Result: {result}")
    
    print("4. Saving state to slot 1...")
    result = api.save_state(slot=1)
    print(f"   Result: {result}")
    
    return api

def example_multi_instance():
    """Example: Control multiple RetroArch instances"""
    print("\n🎮 Multi-Instance Control Example")
    print("-" * 40)
    
    # Connect to multiple instances
    multi = MultiInstanceAPI(num_instances=3, port_base=55355)
    
    print("1. Resetting all instances...")
    results = multi.reset_all()
    for instance_id, result in results.items():
        print(f"   Instance {instance_id}: {result}")
    
    print("2. Enabling fast forward on all...")
    results = multi.fast_forward_all()
    for instance_id, result in results.items():
        print(f"   Instance {instance_id}: {result}")
    
    print("3. Taking screenshots of all...")
    results = multi.screenshot_all()
    for instance_id, result in results.items():
        print(f"   Instance {instance_id}: {result}")
    
    return multi

def example_pokemon_automation():
    """Example: Pokemon shiny hunting automation"""
    print("\n✨ Pokemon Shiny Hunting Example")
    print("-" * 40)
    
    # Use instance 1 for Pokemon automation
    api = RetroArchAPI(port=55356)
    
    print("Starting Pokemon automation sequence...")
    
    # 1. Enable fast forward for quick gameplay
    print("1. Enabling fast forward...")
    api.fast_forward()
    
    # 2. Save initial state
    print("2. Saving initial state...")
    api.save_state(slot=0)
    
    # 3. Simulate automation loop
    for attempt in range(1, 4):  # Just 3 attempts for example
        print(f"\n--- Attempt {attempt} ---")
        
        # Reset to saved state
        print("  Loading save state...")
        api.load_state(slot=0)
        time.sleep(0.5)  # Brief pause
        
        # Here you would add your Pokemon encounter logic
        # For example: walk to grass, encounter Pokemon, check if shiny
        
        # Take screenshot for analysis
        print("  Taking screenshot for analysis...")
        api.screenshot()
        
        # In real automation, you'd analyze the screenshot here
        # For demo, we'll just continue
        
        print(f"  Attempt {attempt} complete")
    
    print("\nPokemon automation example finished!")
    return api

def example_convenience_functions():
    """Example: Using convenience functions"""
    print("\n⚡ Convenience Functions Example")
    print("-" * 40)
    
    print("1. Quick reset of instance 2...")
    result = quick_reset(instance_id=2, port_base=55355)
    print(f"   Result: {result}")
    
    print("2. Quick fast forward of instance 1...")
    result = quick_fast_forward(instance_id=1, port_base=55355)
    print(f"   Result: {result}")

def example_error_handling():
    """Example: Proper error handling"""
    print("\n🛡️  Error Handling Example")
    print("-" * 40)
    
    # Try to connect to a non-existent instance
    api = RetroArchAPI(port=99999)  # This port likely won't exist
    
    print("1. Attempting command on non-existent port...")
    result = api.reset_game()
    
    if result['status'] == 'failed':
        print(f"   ❌ Command failed: {result['error']}")
        print("   This is expected - no RetroArch on port 99999")
    else:
        print(f"   ✅ Unexpected success: {result}")
    
    # Compare with UDP (which doesn't give connection errors)
    print("2. Trying UDP command...")
    result = api.send_udp_command('RESET')
    print(f"   UDP Result: {result}")
    print("   Note: UDP always shows 'sent' even if nothing is listening")

def example_batch_operations():
    """Example: Batch operations across instances"""
    print("\n📦 Batch Operations Example")
    print("-" * 40)
    
    multi = MultiInstanceAPI(num_instances=5, port_base=55355)
    
    # Custom batch operation
    print("1. Sending custom command to all instances...")
    results = multi.command_all('PAUSE_TOGGLE')
    
    successful = sum(1 for r in results.values() if r.get('status') == 'ok')
    print(f"   Successful commands: {successful}/{len(results)}")
    
    # Individual instance control
    print("2. Controlling specific instances...")
    
    # Reset only instances 1 and 3
    for instance_id in [1, 3]:
        api = multi.get_instance(instance_id)
        if api:
            result = api.reset_game()
            print(f"   Instance {instance_id} reset: {result}")

def main():
    """Run all examples"""
    print("🎮 RetroArch HTTP API Examples")
    print("=" * 50)
    
    try:
        # Run examples
        example_single_instance()
        example_multi_instance()
        example_pokemon_automation()
        example_convenience_functions()
        example_error_handling()
        example_batch_operations()
        
        print("\n🎉 All examples completed!")
        print("\n💡 Tips:")
        print("   - Start RetroArch instances first for real testing")
        print("   - Use ports 55356, 55357, 55358, etc.")
        print("   - Enable network commands in RetroArch config")
        
    except KeyboardInterrupt:
        print("\n⏹️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")

if __name__ == '__main__':
    main() 