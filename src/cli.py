"""Command-line interface for the self-editing agent."""

import click
import sys
from pathlib import Path

from src.core.agent import SelfEditingAgent
from src.core.config import ConfigManager
from src.core.state import StateManager


@click.group()
@click.version_option(version="0.2.0", prog_name="agent")
def main():
    """Self-editing AI agent that can modify its own codebase."""
    pass


@main.command()
@click.option('--name', default='SelfEditingAgent', help='Agent name')
@click.option('--config', default=None, help='Path to config file')
@click.option('--state-dir', default=None, help='Path to state directory')
def start(name, config, state_dir):
    """Start the self-editing agent."""
    agent = SelfEditingAgent(
        name=name,
        config_path=config,
        state_dir=state_dir
    )
    
    click.echo(f"Starting {agent.name}...")
    click.echo(f"Agent ID: {agent.agent_id}")
    
    # Show status
    status = agent.get_status()
    click.echo(f"Version: {status['version']}")
    click.echo(f"Total edits: {status['total_edits']}")
    click.echo(f"Total restarts: {status['total_restarts']}")
    
    # Check if git repo
    from src.version_control.git_manager import GitManager
    git_manager = GitManager()
    
    if git_manager.is_git_repo():
        click.echo(f"Git branch: {git_manager.get_branch()}")
    else:
        click.echo("Not a git repository")
    
    click.echo("\nAgent ready. Press Ctrl+C to stop.")
    
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        click.echo("\nShutting down...")
        agent.restart("User interrupt")


@main.command()
def status():
    """Show agent status."""
    state_manager = StateManager()
    state = state_manager.load()
    
    if not state:
        click.echo("No agent state found")
        return
    
    click.echo(f"Name: {state.name}")
    click.echo(f"Agent ID: {state.agent_id}")
    click.echo(f"Version: {state.current_version}")
    click.echo(f"Total edits: {state.total_edits}")
    click.echo(f"Total restarts: {state.total_restarts}")
    
    if state.last_edited_at:
        click.echo(f"Last edited: {state.last_edited_at}")
    
    # Show recent edits
    recent_edits = state.get_edit_history(limit=5)
    if recent_edits:
        click.echo("\nRecent edits:")
        for edit in recent_edits:
            click.echo(f"  - {edit.file_path}: {edit.reason}")


@main.command()
@click.argument('file_path')
@click.option('--reason', required=True, help='Reason for the edit')
@click.option('--dry-run', is_flag=True, help='Show what would be changed')
def edit(file_path, reason, dry_run):
    """Edit a file and record the change."""
    agent = SelfEditingAgent()
    
    if not Path(file_path).exists():
        click.echo(f"File not found: {file_path}")
        sys.exit(1)
    
    # Read current content
    with open(file_path, 'r') as f:
        current_content = f.read()
    
    # Show what would change (dry run)
    if dry_run:
        click.echo(f"Would edit: {file_path}")
        click.echo(f"Reason: {reason}")
        click.echo("\nCurrent content:")
        click.echo(current_content)
        return
    
    # For demo, just show the edit would happen
    click.echo(f"Would edit {file_path} with reason: {reason}")
    click.echo("(In a real implementation, this would prompt for new content)")


@main.command()
def history():
    """Show edit history."""
    state_manager = StateManager()
    state = state_manager.load()
    
    if not state:
        click.echo("No agent state found")
        return
    
    history = state.edit_history
    
    if not history:
        click.echo("No edit history")
        return
    
    click.echo(f"Total edits: {len(history)}\n")
    
    for edit in reversed(history[-20:]):  # Show last 20
        click.echo(f"Edit {edit.edit_id}: {edit.file_path}")
        click.echo(f"  Reason: {edit.reason}")
        click.echo(f"  Time: {edit.timestamp}")
        click.echo()


@main.command()
def rollback():
    """Rollback to previous state."""
    click.echo("Rollback functionality not yet implemented")


@main.command()
def restart():
    """Perform a graceful restart."""
    agent = SelfEditingAgent()
    click.echo(f"Restarting {agent.name}...")
    agent.restart("CLI restart")


if __name__ == '__main__':
    main()
