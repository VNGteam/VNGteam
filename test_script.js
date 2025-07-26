#!/usr/bin/env node
/**
 * Test JavaScript script for CMD Manager Application
 * This script demonstrates Node.js script management capabilities
 */

const readline = require('readline');

// Create readline interface for handling input
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

let counter = 0;
let isRunning = true;

function getCurrentTime() {
    return new Date().toLocaleTimeString();
}

function log(message) {
    console.log(`[${getCurrentTime()}] ${message}`);
}

function logError(message) {
    console.error(`[${getCurrentTime()}] ERROR: ${message}`);
}

function handleUserInput(input) {
    const command = input.trim().toLowerCase();
    
    switch(command) {
        case 'help':
            console.log('📚 Available JavaScript commands:');
            console.log('   help    - Show this help message');
            console.log('   status  - Show current status');
            console.log('   info    - Show Node.js information');
            console.log('   math    - Perform random calculation');
            console.log('   memory  - Show memory usage');
            console.log('   quit    - Exit the script');
            break;
            
        case 'status':
            log(`📈 Status: Running, iteration #${counter}`);
            log(`🔄 Process uptime: ${process.uptime().toFixed(2)} seconds`);
            break;
            
        case 'info':
            console.log('ℹ️  Node.js Information:');
            console.log(`   Node version: ${process.version}`);
            console.log(`   Platform: ${process.platform}`);
            console.log(`   Architecture: ${process.arch}`);
            console.log(`   PID: ${process.pid}`);
            break;
            
        case 'math':
            const a = Math.floor(Math.random() * 100);
            const b = Math.floor(Math.random() * 100);
            const operations = ['+', '-', '*', '/'];
            const op = operations[Math.floor(Math.random() * operations.length)];
            let result;
            
            switch(op) {
                case '+': result = a + b; break;
                case '-': result = a - b; break;
                case '*': result = a * b; break;
                case '/': result = (a / b).toFixed(2); break;
            }
            
            console.log(`🧮 Math: ${a} ${op} ${b} = ${result}`);
            break;
            
        case 'memory':
            const usage = process.memoryUsage();
            console.log('💾 Memory Usage:');
            console.log(`   RSS: ${(usage.rss / 1024 / 1024).toFixed(2)} MB`);
            console.log(`   Heap Used: ${(usage.heapUsed / 1024 / 1024).toFixed(2)} MB`);
            console.log(`   Heap Total: ${(usage.heapTotal / 1024 / 1024).toFixed(2)} MB`);
            break;
            
        case 'quit':
            log('👋 Goodbye from JavaScript!');
            isRunning = false;
            process.exit(0);
            break;
            
        default:
            console.log(`❓ Unknown command: '${input}'`);
            console.log("💡 Type 'help' for available commands");
    }
}

// Handle input from CMD Manager
rl.on('line', handleUserInput);

// Main execution loop
function main() {
    log('🚀 JavaScript Test Script Started!');
    log('📝 This Node.js script demonstrates:');
    log('   - Continuous output generation');
    log('   - Interactive command handling');
    log('   - Memory and system information');
    log('   - Mathematical operations');
    console.log('-'.repeat(50));
    
    const interval = setInterval(() => {
        if (!isRunning) {
            clearInterval(interval);
            return;
        }
        
        counter++;
        
        if (counter % 15 === 0) {
            log(`🔢 JavaScript milestone: ${counter}`);
        } else if (counter % 10 === 0) {
            log(`📊 Node.js is running smoothly - iteration ${counter}`);
        } else if (counter % 7 === 0) {
            log('💡 Tip: JavaScript is great for async operations!');
        } else if (counter % 5 === 0) {
            // Simulate async operation
            log('⚙️  Simulating async operation...');
            setTimeout(() => {
                log('✅ Async operation completed!');
            }, 1000);
        } else {
            log(`📈 Regular JS output #${counter}`);
        }
        
        // Simulate some events
        if (counter === 20) {
            log('⚠️  JavaScript warning simulation');
        } else if (counter === 30) {
            logError('This is a simulated JavaScript error');
        } else if (counter === 40) {
            log('🎉 JavaScript script running excellently!');
        }
        
        // Reset counter after reaching 100
        if (counter >= 100) {
            log('🏁 JavaScript test cycle completed! Restarting...');
            counter = 0;
        }
        
    }, 3000); // 3 second intervals
    
    // Handle process termination
    process.on('SIGINT', () => {
        log('\n⛔ JavaScript script interrupted');
        clearInterval(interval);
        process.exit(0);
    });
    
    process.on('SIGTERM', () => {
        log('🔚 JavaScript script terminated');
        clearInterval(interval);
        process.exit(0);
    });
}

// Start the script
main();