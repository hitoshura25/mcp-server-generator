"""Tests for git username detection and prefix application."""

from unittest.mock import patch, MagicMock
import subprocess
from hitoshura25_mcp_server_generator.git_utils import (
    get_github_username,
    sanitize_username,
    apply_prefix,
)


class TestGetGitHubUsername:
    """Tests for username detection from git configuration."""

    def test_github_user_config(self):
        """Test detection from github.user config (highest priority)."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                stdout='hitoshura25\n',
                returncode=0
            )
            assert get_github_username() == 'hitoshura25'
            mock_run.assert_called_once()

    def test_remote_url_ssh(self):
        """Test detection from SSH remote URL."""
        with patch('subprocess.run') as mock_run:
            # First call (github.user) fails, second (remote URL) succeeds
            mock_run.side_effect = [
                subprocess.CalledProcessError(1, 'git'),
                MagicMock(
                    stdout='git@github.com:hitoshura25/repo.git\n',
                    returncode=0
                )
            ]
            assert get_github_username() == 'hitoshura25'
            assert mock_run.call_count == 2

    def test_remote_url_https(self):
        """Test detection from HTTPS remote URL."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = [
                subprocess.CalledProcessError(1, 'git'),  # github.user fails
                MagicMock(
                    stdout='https://github.com/hitoshura25/repo.git\n',
                    returncode=0
                )
            ]
            assert get_github_username() == 'hitoshura25'

    def test_user_name_fallback(self):
        """Test fallback to user.name (sanitized)."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = [
                subprocess.CalledProcessError(1, 'git'),  # github.user fails
                subprocess.CalledProcessError(1, 'git'),  # remote.origin.url fails
                MagicMock(
                    stdout='John Smith\n',
                    returncode=0
                )
            ]
            assert get_github_username() == 'john-smith'
            assert mock_run.call_count == 3

    def test_no_git_available(self):
        """Test when git is not available."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = FileNotFoundError()
            assert get_github_username() is None

    def test_all_methods_fail(self):
        """Test when all detection methods fail."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, 'git')
            assert get_github_username() is None

    def test_timeout_handling(self):
        """Test timeout handling in git commands."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired('git', 5)
            assert get_github_username() is None

    def test_empty_responses(self):
        """Test handling of empty git responses."""
        with patch('subprocess.run') as mock_run:
            # All commands return empty strings
            mock_run.return_value = MagicMock(stdout='', returncode=0)
            assert get_github_username() is None


class TestSanitizeUsername:
    """Tests for username sanitization."""

    def test_lowercase_conversion(self):
        """Test uppercase to lowercase conversion."""
        assert sanitize_username('JOHN') == 'john'
        assert sanitize_username('JoHn') == 'john'

    def test_space_to_hyphen(self):
        """Test space to hyphen conversion."""
        assert sanitize_username('John Smith') == 'john-smith'
        assert sanitize_username('John  Smith') == 'john-smith'  # Multiple spaces

    def test_dot_to_hyphen(self):
        """Test dot to hyphen conversion."""
        assert sanitize_username('John.Smith') == 'john-smith'
        assert sanitize_username('J.Q.Public') == 'j-q-public'

    def test_remove_invalid_chars(self):
        """Test removal of invalid characters."""
        assert sanitize_username('john@smith') == 'johnsmith'
        assert sanitize_username('john!smith#') == 'johnsmith'
        assert sanitize_username('john_smith') == 'johnsmith'

    def test_strip_hyphens(self):
        """Test stripping leading/trailing hyphens."""
        assert sanitize_username('-john-') == 'john'
        assert sanitize_username('--john--') == 'john'

    def test_consecutive_hyphens(self):
        """Test removal of consecutive hyphens."""
        assert sanitize_username('john---smith') == 'john-smith'
        assert sanitize_username('john--q--smith') == 'john-q-smith'

    def test_combined_transformations(self):
        """Test multiple transformations together."""
        assert sanitize_username('John Q. Smith Jr.') == 'john-q-smith-jr'
        assert sanitize_username('  John  Smith  ') == 'john-smith'
        assert sanitize_username('john@example.com') == 'johnexample-com'  # Dot → hyphen, @ removed

    def test_already_sanitized(self):
        """Test already sanitized names."""
        assert sanitize_username('john-smith') == 'john-smith'
        assert sanitize_username('hitoshura25') == 'hitoshura25'

    def test_numbers_preserved(self):
        """Test that numbers are preserved."""
        assert sanitize_username('user123') == 'user123'
        assert sanitize_username('John Smith 3rd') == 'john-smith-3rd'

    def test_edge_cases(self):
        """Test edge cases."""
        assert sanitize_username('') == ''
        assert sanitize_username('---') == ''
        assert sanitize_username('123') == '123'


class TestApplyPrefix:
    """Tests for prefix application to package names."""

    def test_auto_mode_with_detection(self):
        """Test AUTO mode when username is detected."""
        with patch('hitoshura25_mcp_server_generator.git_utils.get_github_username') as mock_get:
            mock_get.return_value = 'hitoshura25'
            pkg, imp = apply_prefix('my-tool', 'AUTO')
            assert pkg == 'hitoshura25-my-tool'
            assert imp == 'hitoshura25_my_tool'

    def test_auto_mode_no_detection(self):
        """Test AUTO mode when username cannot be detected."""
        with patch('hitoshura25_mcp_server_generator.git_utils.get_github_username') as mock_get:
            mock_get.return_value = None
            pkg, imp = apply_prefix('my-tool', 'AUTO')
            # Should fallback to no prefix
            assert pkg == 'my-tool'
            assert imp == 'my_tool'

    def test_custom_prefix(self):
        """Test custom prefix application."""
        pkg, imp = apply_prefix('my-tool', 'acme')
        assert pkg == 'acme-my-tool'
        assert imp == 'acme_my_tool'

    def test_custom_prefix_sanitized(self):
        """Test that custom prefixes are sanitized."""
        pkg, imp = apply_prefix('my-tool', 'ACME Corp')
        assert pkg == 'acme-corp-my-tool'
        assert imp == 'acme_corp_my_tool'

    def test_none_mode(self):
        """Test NONE mode (no prefix)."""
        pkg, imp = apply_prefix('my-tool', 'NONE')
        assert pkg == 'my-tool'
        assert imp == 'my_tool'

    def test_hyphen_to_underscore_conversion(self):
        """Test hyphen to underscore conversion for imports."""
        pkg, imp = apply_prefix('my-tool', 'my-prefix')
        assert pkg == 'my-prefix-my-tool'
        assert imp == 'my_prefix_my_tool'

    def test_complex_package_names(self):
        """Test with complex package names."""
        pkg, imp = apply_prefix('my-complex-tool-name', 'acme')
        assert pkg == 'acme-my-complex-tool-name'
        assert imp == 'acme_my_complex_tool_name'

    def test_package_with_numbers(self):
        """Test package names with numbers."""
        pkg, imp = apply_prefix('tool-v2', 'acme')
        assert pkg == 'acme-tool-v2'
        assert imp == 'acme_tool_v2'

    def test_prefix_with_numbers(self):
        """Test prefixes containing numbers."""
        pkg, imp = apply_prefix('my-tool', 'user123')
        assert pkg == 'user123-my-tool'
        assert imp == 'user123_my_tool'

    def test_return_type(self):
        """Test that return type is tuple of strings."""
        result = apply_prefix('my-tool', 'acme')
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)
        assert isinstance(result[1], str)

    def test_auto_with_different_usernames(self):
        """Test AUTO mode with various username formats."""
        with patch('hitoshura25_mcp_server_generator.git_utils.get_github_username') as mock_get:
            # Simple username
            mock_get.return_value = 'user'
            pkg, imp = apply_prefix('tool', 'AUTO')
            assert pkg == 'user-tool'
            assert imp == 'user_tool'

            # Username with hyphens
            mock_get.return_value = 'user-name'
            pkg, imp = apply_prefix('tool', 'AUTO')
            assert pkg == 'user-name-tool'
            assert imp == 'user_name_tool'

            # Username with numbers
            mock_get.return_value = 'user123'
            pkg, imp = apply_prefix('tool', 'AUTO')
            assert pkg == 'user123-tool'
            assert imp == 'user123_tool'


class TestIntegrationScenarios:
    """Integration tests for complete workflows."""

    def test_full_workflow_auto_detection(self):
        """Test complete workflow with AUTO detection."""
        with patch('hitoshura25_mcp_server_generator.git_utils.get_github_username') as mock_get:
            mock_get.return_value = 'testuser'

            # Generate package name
            pkg, imp = apply_prefix('my-mcp-server', 'AUTO')

            # Verify results are usable
            assert pkg == 'testuser-my-mcp-server'
            assert imp == 'testuser_my_mcp_server'

            # Verify import name can be used as Python identifier
            assert imp.isidentifier()

    def test_full_workflow_custom_prefix(self):
        """Test complete workflow with custom prefix."""
        pkg, imp = apply_prefix('calculator-tool', 'acme')

        assert pkg == 'acme-calculator-tool'
        assert imp == 'acme_calculator_tool'
        assert imp.isidentifier()

    def test_full_workflow_no_prefix(self):
        """Test complete workflow without prefix."""
        pkg, imp = apply_prefix('unique-package-name', 'NONE')

        assert pkg == 'unique-package-name'
        assert imp == 'unique_package_name'
        assert imp.isidentifier()
