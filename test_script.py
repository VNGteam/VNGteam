#!/usr/bin/env python3
"""
Test script for CMD Manager Application
This script demonstrates various features that can be tested with the manager.
"""

import time
import sys
import random
from datetime import datetime

def main():
    """Main function that runs various test scenarios"""
    print("🚀 Test Script Started!")
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📝 This script will demonstrate various features:")
    print("   - Continuous output")
    print("   - Interactive input handling")
    print("   - Error generation")
    print("   - Long-running process simulation")
    print("-" * 50)
    
    counter = 0
    
    try:
        while True:
            counter += 1
            current_time = datetime.now().strftime('%H:%M:%S')
            
            # Different types of output every few iterations
            if counter % 10 == 0:
                print(f"🔢 Counter milestone: {counter} at {current_time}")
            elif counter % 7 == 0:
                print(f"💡 Random tip: Keep your scripts organized!")
            elif counter % 5 == 0:
                # Simulate some processing
                processing_time = random.uniform(0.5, 2.0)
                print(f"⚙️  Processing for {processing_time:.1f} seconds...")
                time.sleep(processing_time)
                print(f"✅ Processing complete!")
            else:
                print(f"📊 Regular output #{counter} - {current_time}")
            
            # Check for user input (non-blocking)
            try:
                # This will work when commands are sent from the manager
                user_input = sys.stdin.readline().strip()
                if user_input:
                    handle_user_input(user_input, counter)
            except:
                pass  # No input available
            
            # Simulate different scenarios
            if counter == 15:
                print("⚠️  Simulating a warning condition...")
            elif counter == 25:
                print("❌ ERROR: This is a simulated error for testing", file=sys.stderr)
            elif counter == 35:
                print("🎉 Milestone reached! Script is working well.")
            
            # Sleep between outputs
            time.sleep(2)
            
            # Stop after a reasonable number for testing
            if counter >= 100:
                print("🏁 Test completed successfully! Restarting count...")
                counter = 0
                
    except KeyboardInterrupt:
        print("\n⛔ Script interrupted by user")
    except Exception as e:
        print(f"💥 Unexpected error: {e}", file=sys.stderr)
    finally:
        print(f"🔚 Test script ending at {datetime.now().strftime('%H:%M:%S')}")

def handle_user_input(user_input, current_counter):
    """Handle commands sent from the CMD Manager"""
    command = user_input.lower().strip()
    
    if command == "help":
        print("📚 Available commands:")
        print("   help    - Show this help message")
        print("   status  - Show current status")
        print("   error   - Generate a test error")
        print("   info    - Show script information")
        print("   random  - Generate random data")
        print("   quit    - Exit the script")
        
    elif command == "status":
        print(f"📈 Status: Running normally, iteration #{current_counter}")
        print(f"⏱️  Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    elif command == "error":
        print("🧪 Generating test error...", file=sys.stderr)
        print("ERROR: This is a deliberate test error!", file=sys.stderr)
        
    elif command == "info":
        print("ℹ️  Script Information:")
        print(f"   Script: {__file__}")
        print(f"   Python: {sys.version}")
        print(f"   PID: {sys.version}")
        
    elif command == "random":
        random_number = random.randint(1, 1000)
        random_word = random.choice(["awesome", "fantastic", "great", "excellent", "wonderful"])
        print(f"🎲 Random number: {random_number}")
        print(f"🎪 Random word: {random_word}")
        
    elif command == "quit":
        print("👋 Goodbye! Exiting script...")
        sys.exit(0)
        
    else:
        print(f"❓ Unknown command: '{user_input}'")
        print("💡 Type 'help' for available commands")

if __name__ == "__main__":
    main()