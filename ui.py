"""
UI presentation layer for displaying market data.
"""

import sys
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class MarketUI:
    """UI handler for displaying market data."""
    
    @staticmethod
    def show_status(message: str):
        """Show a status message with spinner."""
        return console.status(f"[bold green]{message}")
    
    @staticmethod
    def print_success(message: str):
        """Print a success message."""
        console.print(f"[bold green]✓[/bold green] {message}")
    
    @staticmethod
    def print_warning(message: str):
        """Print a warning message."""
        console.print(f"[yellow]⚠[/yellow] {message}")
    
    @staticmethod
    def print_error(message: str):
        """Print an error message."""
        console.print(f"[bold red]Error:[/bold red] {message}")
    
    @staticmethod
    def print_info(message: str):
        """Print an info message."""
        console.print(f"[cyan]{message}[/cyan]")
    
    @staticmethod
    def print_dim(message: str):
        """Print a dimmed message."""
        console.print(f"[dim]{message}[/dim]")
    
    @staticmethod
    def show_datacenters(datacenters: List[Dict]):
        """Display datacenters in a table."""
        if not datacenters:
            MarketUI.print_warning("No datacenters found.")
            return
        
        table = Table(title="Final Fantasy XIV Datacenters", show_header=True, header_style="bold magenta")
        table.add_column("Datacenter", style="cyan", no_wrap=True)
        table.add_column("Region", style="green")
        table.add_column("Worlds", style="yellow")
        
        # Sort datacenters by region and name
        sorted_dcs = sorted(datacenters, key=lambda x: (x.get('region', ''), x.get('name', '')))
        
        for dc in sorted_dcs:
            name = dc.get('name', 'N/A')
            region = dc.get('region', 'N/A')
            worlds = dc.get('worlds', [])
            worlds_str = f"{len(worlds)} worlds" if worlds else "No worlds"
            table.add_row(name, region, worlds_str)
        
        console.print(table)
        console.print(f"\n[bold]Total:[/bold] {len(datacenters)} datacenters")
    
    @staticmethod
    def show_top_items(world: str, items: List[Dict], format_time_func):
        """Display top items table."""
        if not items:
            MarketUI.print_warning(f"No data available for {world}. Run 'update' first.")
            return
        
        table = Table(title=f"Top {len(items)} Items by Sales Volume on {world}",
                     show_header=True, header_style="bold magenta")
        table.add_column("Rank", style="cyan", width=6)
        table.add_column("Item", style="yellow")
        table.add_column("Daily Sales", justify="right", style="green")
        table.add_column("Avg Price", justify="right", style="magenta")
        table.add_column("Last Updated", style="dim")
        
        for idx, item in enumerate(items, 1):
            time_str = format_time_func(item['last_updated'])
            
            display_name = item.get('item_name') or str(item['item_id'])
            table.add_row(
                str(idx),
                display_name,
                f"{item['sale_velocity']:.2f}" if item['sale_velocity'] else "N/A",
                f"{item['average_price']:,.0f} gil" if item['average_price'] else "N/A",
                time_str
            )
        
        console.print(table)
        console.print(f"\n[dim]Snapshot date: {items[0]['snapshot_date']}[/dim]")
    
    @staticmethod
    def show_item_report_header(world: str, item_id: int, days_count: int):
        """Display header for item report."""
        console.print(f"\n[bold cyan]Item {item_id} on {world}[/bold cyan]")
        console.print(f"[dim]Historical data for the last {days_count} days[/dim]\n")
    
    @staticmethod
    def show_item_report_table(snapshots: List[Dict]):
        """Display item report table."""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Date", style="cyan")
        table.add_column("Daily Sales", justify="right", style="green")
        table.add_column("Avg Price", justify="right", style="yellow")
        table.add_column("Min Price", justify="right")
        table.add_column("Max Price", justify="right")
        table.add_column("Listings", justify="right")
        
        for snapshot in reversed(snapshots):  # Show oldest to newest
            table.add_row(
                snapshot['snapshot_date'],
                f"{snapshot['sale_velocity']:.2f}" if snapshot['sale_velocity'] else "N/A",
                f"{snapshot['average_price']:,.0f}" if snapshot['average_price'] else "N/A",
                f"{snapshot['min_price']:,}" if snapshot['min_price'] else "N/A",
                f"{snapshot['max_price']:,}" if snapshot['max_price'] else "N/A",
                str(snapshot['total_listings']) if snapshot['total_listings'] else "0"
            )
        
        console.print(table)
    
    @staticmethod
    def show_trends(trends: Dict[str, float]):
        """Display trend information."""
        if 'velocity_change' in trends:
            velocity_change = trends['velocity_change']
            velocity_emoji = "📈" if velocity_change > 0 else "📉"
            console.print(f"\n{velocity_emoji} Sales velocity trend: {velocity_change:+.1f}%")
        
        if 'price_change' in trends:
            price_change = trends['price_change']
            price_emoji = "💰" if price_change > 0 else "💸"
            console.print(f"{price_emoji} Price trend: {price_change:+.1f}%")

    @staticmethod
    def show_tracked_worlds(worlds: List[Dict]):
        """Display tracked worlds configuration in a table."""
        table = Table(title="Tracked Worlds", show_header=True, header_style="bold magenta")
        table.add_column("World ID", style="cyan")
        table.add_column("World Name", style="yellow")
        table.add_column("Added", style="green")
        
        if not worlds:
            MarketUI.print_warning("No tracked worlds configured.")
        else:
            for w in worlds:
                table.add_row(
                    str(w.get('world_id')),
                    w.get('world_name') or 'Unknown',
                    (w.get('added_at') or '')
                )
            console.print(table)
    
    @staticmethod
    def exit_with_error(message: str, exit_code: int = 1):
        """Print error and exit."""
        MarketUI.print_error(message)
        sys.exit(exit_code)
