# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: [YOUR-EMAIL@example.com]

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

Please include the following information:

- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

## Security Considerations

PC Assistant handles sensitive system operations. Please be aware:

### Administrator Privileges
- Many features require administrator privileges
- Always run from a trusted source
- Verify checksums of downloaded releases

### Registry Operations
- Registry modifications are backed up automatically
- Backups are stored in `registry_backups/` directory
- Always review changes before applying

### File Deletion
- Secure deletion is irreversible
- Multiple confirmation dialogs are shown
- Test with non-critical files first

### Data Privacy
- No data is collected or transmitted
- All operations are performed locally
- Logs are stored locally in `logs/` directory

## Best Practices for Users

1. **Download from Official Sources**
   - Only download releases from the official GitHub repository
   - Verify SHA256 checksums provided with releases

2. **Run as Administrator Carefully**
   - Only grant administrator privileges when needed
   - Review all operations before confirming

3. **Backup Important Data**
   - Create system restore points before major operations
   - Back up important files before using secure deletion

4. **Keep Updated**
   - Use the latest version for security patches
   - Check for updates regularly

## Disclosure Policy

When we receive a security bug report, we will:

1. Confirm the problem and determine affected versions
2. Audit code to find similar problems
3. Prepare fixes for all supported versions
4. Release new versions as soon as possible

## Comments on This Policy

If you have suggestions on how this process could be improved, please submit a pull request.
