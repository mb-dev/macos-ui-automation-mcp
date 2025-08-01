# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | ✅ Yes              |
| < Latest| ❌ No               |

## Reporting a Vulnerability

If you discover a security vulnerability in Playwright MCP for macOS, please report it responsibly:

### For Non-Critical Issues
- Open a GitHub issue with the `security` label
- Provide as much detail as possible about the vulnerability
- Include steps to reproduce if applicable

### For Critical Security Issues
- **DO NOT** open a public GitHub issue
- Email the maintainer directly (check GitHub profile for contact)
- Include "SECURITY" in the subject line
- Provide detailed information about the vulnerability

## Security Considerations

This tool interacts with macOS accessibility APIs and requires special permissions:

### Accessibility Permissions
- The tool requires accessibility permissions to function
- These permissions must be granted to the **parent application** (Terminal, VS Code, Claude Code)
- Never grant accessibility permissions to untrusted applications

### MCP Server Security
- The MCP server runs locally and does not make external network requests
- All UI automation happens locally on your machine
- No data is transmitted to external servers

### Code Execution
- This tool can interact with any macOS application that has accessibility APIs
- Use caution when running automation scripts on sensitive applications
- Always review automation scripts before execution

### Dependencies
- We regularly scan dependencies for known vulnerabilities
- Security scans are run automatically in our CI pipeline
- Update to the latest version to get security patches

## Best Practices

When using this tool:

1. **Principle of Least Privilege**: Only grant accessibility permissions when needed
2. **Code Review**: Review any automation scripts before running them
3. **Update Regularly**: Keep the tool updated to get the latest security patches
4. **Trusted Sources**: Only run automation scripts from trusted sources
5. **Test Environment**: Test automation scripts in a safe environment first

## Acknowledgments

We appreciate security researchers and users who report vulnerabilities responsibly.