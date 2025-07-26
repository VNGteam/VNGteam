# Advanced CMD/Script Manager & Cloudflare DNS Updater v2.0

A powerful cross-platform application for managing multiple scripts and automatically updating Cloudflare DNS records when your public IP changes.

## 🌟 Features

### Script Management
- **Multi-script support**: Python (.py), JavaScript (.js), Batch (.bat), Shell (.sh)
- **Real-time output monitoring**: See script output in dedicated text areas
- **Interactive command sending**: Send commands to running scripts
- **Auto-start capability**: Configure scripts to start automatically
- **Process management**: Start, stop, and restart scripts individually or all at once
- **Enhanced script configuration**: Set working directories, descriptions, and more

### Cloudflare DNS Management
- **Automatic IP monitoring**: Continuously check for public IP changes
- **Multi-account support**: Manage multiple Cloudflare accounts
- **Multi-domain support**: Update multiple domains/subdomains per account
- **Configurable check intervals**: Set custom intervals for IP checking
- **Real-time status updates**: See the status of DNS updates
- **Force update capability**: Manually trigger DNS updates

### Enhanced User Interface
- **Modern tabbed interface**: Organized tabs for Scripts, Cloudflare, and Logs
- **TreeView displays**: Better organization and management of scripts and domains
- **Status indicators**: Visual indicators for script and DNS status
- **Menu bar**: Easy access to all features
- **Status bar**: Quick overview of current state

### Advanced Features
- **Cross-platform compatibility**: Works on Windows, Linux, and macOS
- **Enhanced error handling**: Comprehensive error logging and user feedback
- **Configuration management**: Import/export configurations
- **Auto-save functionality**: Automatic configuration saving
- **Startup integration**: Add to system startup (Windows only)
- **Comprehensive logging**: Detailed logs with timestamp
- **Thread-safe operations**: Proper handling of concurrent operations

## 🔧 Installation

### Prerequisites
- Python 3.7 or higher
- tkinter (usually included with Python)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Dependencies
- `requests`: For HTTP requests to IP services and Cloudflare API
- `aiohttp`: For asynchronous HTTP operations
- `typing_extensions`: For enhanced type hints

## 🚀 Quick Start

### Running the Application
```bash
python cmd_manager_app.py
```

### Adding Scripts
1. Go to the **Scripts** tab
2. Click **Add Script**
3. Select your script file (.py, .js, .bat, .sh)
4. Configure script settings:
   - Script name
   - Auto-run on startup
   - Working directory
   - Description
5. Click **Save**

### Configuring Cloudflare DNS
1. Go to the **Cloudflare DNS** tab
2. Click **Add Account**
3. Enter your Cloudflare API token
4. Set check interval (in minutes)
5. Add domains by providing:
   - Domain name
   - Zone ID
   - Record ID
   - Record name (subdomain.domain.com)
6. Click **Save**

## 📖 Detailed Usage

### Script Management

#### Supported Script Types
- **Python (.py)**: Uses system Python interpreter
- **JavaScript (.js)**: Requires Node.js
- **Batch (.bat)**: Windows batch files (uses wine on Linux/macOS)
- **Shell (.sh)**: Unix shell scripts

#### Script Controls
- **Start/Stop**: Toggle script execution
- **Auto Run**: Enable automatic startup
- **Send Commands**: Interactive command input
- **Edit Configuration**: Modify script settings

### Cloudflare Integration

#### API Token Setup
1. Log in to Cloudflare dashboard
2. Go to "My Profile" → "API Tokens"
3. Create a token with Zone:DNS:Edit permissions
4. Copy the token for use in the application

#### Getting Zone and Record IDs
Use Cloudflare API or dashboard to find:
- **Zone ID**: Found in domain overview
- **Record ID**: Use API call to list DNS records

### Configuration Management

#### Export Configuration
- File → Export Config
- Saves scripts and Cloudflare settings to JSON file

#### Import Configuration
- File → Import Config
- Load previously saved configuration

## 🔧 Advanced Configuration

### Startup Integration (Windows)
- Tools → Add to Startup: Add application to Windows startup
- Tools → Remove from Startup: Remove from Windows startup

### Logging
- All operations are logged to `cmd_manager.log`
- View real-time logs in the **Logs** tab
- Export logs: Logs tab → Save Logs

### Auto-Save
- Configuration is automatically saved every 5 minutes
- Manual save occurs on application close

## 🛠️ Troubleshooting

### Common Issues

#### Script Won't Start
- Check if the required interpreter is installed (Python, Node.js, etc.)
- Verify script file permissions
- Check working directory settings

#### Cloudflare DNS Not Updating
- Verify API token has correct permissions
- Check Zone ID and Record ID are correct
- Ensure internet connectivity
- Check logs for specific error messages

#### Permission Errors (Linux/macOS)
```bash
chmod +x your_script.sh
```

### Error Logs
Check the **Logs** tab or `cmd_manager.log` file for detailed error information.

## 🔐 Security Considerations

- API tokens are stored in plain text in config.json
- Consider using environment variables for sensitive data
- Regularly rotate Cloudflare API tokens
- Keep the application updated

## 🚧 Platform-Specific Notes

### Windows
- Full startup integration support
- Batch file execution support
- Uses Windows registry for startup management

### Linux/macOS
- Startup integration not available
- Batch files require wine
- Shell scripts require proper permissions

## 📝 Configuration File Format

The configuration is stored in `config.json`:

```json
{
    "scripts": [
        {
            "name": "My Script",
            "path": "/path/to/script.py",
            "auto_run": true,
            "working_dir": "/path/to/working/dir",
            "description": "Script description",
            "status": "stopped",
            "created": "2024-01-01T00:00:00"
        }
    ],
    "cloudflare_accounts": [
        {
            "api_token": "your_api_token",
            "check_interval": 300,
            "domains": [
                {
                    "domain": "example.com",
                    "zone_id": "zone_id",
                    "record_id": "record_id",
                    "record_name": "subdomain.example.com",
                    "ttl": 1,
                    "proxied": true
                }
            ]
        }
    ],
    "version": "2.0",
    "last_saved": "2024-01-01T00:00:00"
}
```

## 🔄 Version History

### v2.0 (Current)
- Complete rewrite with enhanced architecture
- Cross-platform compatibility
- Improved error handling and logging
- Enhanced user interface with TreeView components
- Configuration import/export
- Auto-save functionality
- Thread-safe operations
- Comprehensive documentation

### v1.0 (Original)
- Basic script management
- Cloudflare DNS updates
- Simple GUI interface

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source. Please ensure compliance with all dependencies' licenses.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Create an issue with detailed information

## 🔮 Future Enhancements

- [ ] Encrypted configuration storage
- [ ] Plugin system for custom script types
- [ ] Web interface option
- [ ] Docker containerization
- [ ] Backup and restore functionality
- [ ] Script scheduling capabilities
- [ ] Performance monitoring
- [ ] Notification system
