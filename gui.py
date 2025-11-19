"""
GUI Dashboard for Screen Time Tracker
Modern interface using customtkinter with enhanced UI/UX
"""
import customtkinter as ctk
import threading
import time
from datetime import datetime, timedelta, date
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import numpy as np


class ScreenTimeGUI:
    """Main GUI window for screen time statistics"""
    
    def __init__(self, root, database, tracker_service):
        """
        Initialize GUI
        
        Args:
            root: Tkinter root window
            database: Database instance
            tracker_service: TrackerService instance
        """
        self.root = root
        self.db = database
        self.tracker_service = tracker_service
        
        # Configure customtkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Window setup
        self.root.title("Screen Time Tracker")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        
        # Color scheme
        self.colors = {
            'bg': '#0d1117',
            'card': '#161b22',
            'accent': '#58a6ff',
            'accent_hover': '#79c0ff',
            'text_primary': '#c9d1d9',
            'text_secondary': '#8b949e',
            'success': '#3fb950',
            'warning': '#d29922',
            'danger': '#f85149',
        }
        
        # Initially hide window (show via tray icon)
        self.root.withdraw()
        
        # Selected date for history view
        self.selected_date = None
        
        # Create UI
        self.create_widgets()
        
        # Start update thread
        self.update_thread_running = True
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container with padding
        main_container = ctk.CTkFrame(self.root, fg_color=self.colors['bg'])
        main_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Header bar
        header_frame = ctk.CTkFrame(main_container, fg_color=self.colors['card'], height=80)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="⏱️ Screen Time Dashboard",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=self.colors['text_primary']
        )
        title_label.pack(side="left", padx=30, pady=20)
        
        # Status indicator
        self.status_label = ctk.CTkLabel(
            header_frame,
            text="● Tracking",
            font=ctk.CTkFont(size=14),
            text_color=self.colors['success']
        )
        self.status_label.pack(side="right", padx=30, pady=20)
        
        # Main content area with scroll
        content_scroll = ctk.CTkScrollableFrame(main_container, fg_color=self.colors['bg'])
        content_scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Top stats row (Today and Yesterday)
        stats_row = ctk.CTkFrame(content_scroll, fg_color=self.colors['bg'])
        stats_row.pack(fill="x", pady=(0, 20))
        
        # Today card
        today_card = self.create_stat_card(
            stats_row,
            "Today",
            "0h 0m",
            self.colors['accent'],
            lambda: self.show_date_view(date.today())
        )
        today_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Yesterday card
        yesterday_card = self.create_stat_card(
            stats_row,
            "Yesterday",
            "0h 0m",
            self.colors['text_secondary'],
            lambda: self.show_date_view(date.today() - timedelta(days=1))
        )
        yesterday_card.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        # Main content area (two columns)
        main_content = ctk.CTkFrame(content_scroll, fg_color=self.colors['bg'])
        main_content.pack(fill="both", expand=True, pady=(0, 20))
        
        # Left column - Applications
        left_column = ctk.CTkFrame(main_content, fg_color=self.colors['bg'])
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Applications section
        apps_section = self.create_section_card(left_column, "📱 Top Applications - Today")
        self.apps_scroll = ctk.CTkScrollableFrame(apps_section, fg_color=self.colors['card'])
        self.apps_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Right column - Charts and History
        right_column = ctk.CTkFrame(main_content, fg_color=self.colors['bg'])
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Weekly chart section
        chart_section = self.create_section_card(right_column, "📊 Weekly Overview")
        self.fig = Figure(figsize=(10, 5), facecolor=self.colors['card'])
        self.ax = self.fig.add_subplot(111, facecolor=self.colors['card'])
        self.canvas = FigureCanvasTkAgg(self.fig, chart_section)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Historical timeline section
        history_section = self.create_section_card(left_column, "📅 Recent History")
        self.history_scroll = ctk.CTkScrollableFrame(history_section, fg_color=self.colors['card'])
        self.history_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Yesterday's apps section
        yesterday_apps_section = self.create_section_card(right_column, "📱 Top Applications - Yesterday")
        self.yesterday_apps_scroll = ctk.CTkScrollableFrame(yesterday_apps_section, fg_color=self.colors['card'])
        self.yesterday_apps_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Bottom controls
        controls_frame = ctk.CTkFrame(content_scroll, fg_color=self.colors['card'], height=70)
        controls_frame.pack(fill="x", pady=(10, 0))
        controls_frame.pack_propagate(False)
        
        # Control buttons
        self.pause_button = ctk.CTkButton(
            controls_frame,
            text="⏸ Pause Tracking",
            command=self.toggle_pause,
            width=180,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['accent'],
            hover_color=self.colors['accent_hover']
        )
        self.pause_button.pack(side="left", padx=15, pady=15)
        
        refresh_button = ctk.CTkButton(
            controls_frame,
            text="🔄 Refresh",
            command=self.refresh_data,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=self.colors['card'],
            border_width=1,
            border_color=self.colors['text_secondary']
        )
        refresh_button.pack(side="left", padx=10, pady=15)
        
        hide_button = ctk.CTkButton(
            controls_frame,
            text="⬇️ Hide to Tray",
            command=self.hide_window,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=self.colors['card'],
            border_width=1,
            border_color=self.colors['text_secondary']
        )
        hide_button.pack(side="right", padx=15, pady=15)
        
        # Initial data load
        self.refresh_data()
    
    def create_stat_card(self, parent, title, value, accent_color, command=None):
        """Create a stat card widget"""
        card = ctk.CTkFrame(parent, fg_color=self.colors['card'], corner_radius=15)
        
        # Make it clickable if command provided
        if command:
            card.bind("<Button-1>", lambda e: command())
            for widget in [card]:
                widget.bind("<Enter>", lambda e, w=card: w.configure(fg_color='#1f2937'))
                widget.bind("<Leave>", lambda e, w=card: w.configure(fg_color=self.colors['card']))
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['text_secondary']
        )
        title_label.pack(pady=(20, 5))
        
        # Value
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color=accent_color
        )
        value_label.pack(pady=(0, 20))
        
        # Store reference for updates
        if title == "Today":
            self.today_value_label = value_label
        elif title == "Yesterday":
            self.yesterday_value_label = value_label
        
        return card
    
    def create_section_card(self, parent, title):
        """Create a section card with title"""
        card = ctk.CTkFrame(parent, fg_color=self.colors['card'], corner_radius=15)
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['text_primary']
        )
        title_label.pack(pady=(20, 15), padx=15, anchor="w")
        
        return card
    
    def format_time(self, seconds):
        """Format seconds into readable time string"""
        if seconds < 0:
            seconds = 0
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def format_date_display(self, date_str):
        """Format date string for display"""
        try:
            d = datetime.fromisoformat(date_str).date()
            today = date.today()
            yesterday = today - timedelta(days=1)
            
            if d == today:
                return "Today"
            elif d == yesterday:
                return "Yesterday"
            else:
                return d.strftime("%B %d, %Y")
        except:
            return date_str
    
    def refresh_data(self):
        """Refresh all displayed data"""
        # Get today's stats
        today_stats = self.db.get_today_stats()
        total_seconds = today_stats['total_seconds']
        if hasattr(self, 'today_value_label'):
            self.today_value_label.configure(text=self.format_time(total_seconds))
        
        # Get yesterday's stats
        yesterday_stats = self.db.get_yesterday_stats()
        yesterday_seconds = yesterday_stats['total_seconds']
        if hasattr(self, 'yesterday_value_label'):
            self.yesterday_value_label.configure(text=self.format_time(yesterday_seconds))
        
        # Update today's apps
        self.update_apps_list(today_stats['top_apps'], self.apps_scroll, show_percentage=True)
        
        # Update yesterday's apps
        self.update_apps_list(yesterday_stats['top_apps'], self.yesterday_apps_scroll, show_percentage=False)
        
        # Update chart
        self.update_chart()
        
        # Update history timeline
        self.update_history_timeline()
        
        # Update pause button and status
        if self.tracker_service.is_paused():
            self.pause_button.configure(text="▶ Resume Tracking")
            self.status_label.configure(text="● Paused", text_color=self.colors['warning'])
        else:
            self.pause_button.configure(text="⏸ Pause Tracking")
            self.status_label.configure(text="● Tracking", text_color=self.colors['success'])
    
    def update_apps_list(self, top_apps, scroll_frame, show_percentage=False):
        """Update the applications list"""
        # Clear existing widgets
        for widget in scroll_frame.winfo_children():
            widget.destroy()
        
        if not top_apps:
            no_data_label = ctk.CTkLabel(
                scroll_frame,
                text="No data available yet.",
                font=ctk.CTkFont(size=14),
                text_color=self.colors['text_secondary']
            )
            no_data_label.pack(pady=30)
            return
        
        # Calculate total for percentages
        total_time = sum(app['duration'] for app in top_apps) if show_percentage else None
        
        # Create app items
        for i, app in enumerate(top_apps[:15], 1):
            app_frame = ctk.CTkFrame(scroll_frame, fg_color=self.colors['bg'], corner_radius=8)
            app_frame.pack(fill="x", padx=5, pady=4)
            
            # Left side - Rank and name
            left_frame = ctk.CTkFrame(app_frame, fg_color="transparent")
            left_frame.pack(side="left", fill="x", expand=True, padx=15, pady=10)
            
            # Rank badge
            rank_badge = ctk.CTkLabel(
                left_frame,
                text=f"#{i}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=self.colors['accent'],
                width=35
            )
            rank_badge.pack(side="left", padx=(0, 10))
            
            # App name
            name_label = ctk.CTkLabel(
                left_frame,
                text=app['app_name'],
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color=self.colors['text_primary'],
                anchor="w"
            )
            name_label.pack(side="left", fill="x", expand=True)
            
            # Right side - Time and percentage
            right_frame = ctk.CTkFrame(app_frame, fg_color="transparent")
            right_frame.pack(side="right", padx=15, pady=10)
            
            # Duration
            duration_label = ctk.CTkLabel(
                right_frame,
                text=self.format_time(app['duration']),
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color=self.colors['text_primary'],
                width=80
            )
            duration_label.pack(side="right", padx=(10, 0))
            
            # Percentage bar
            if show_percentage and total_time > 0:
                percentage = (app['duration'] / total_time) * 100
                percentage_label = ctk.CTkLabel(
                    right_frame,
                    text=f"{percentage:.1f}%",
                    font=ctk.CTkFont(size=12),
                    text_color=self.colors['text_secondary'],
                    width=50
                )
                percentage_label.pack(side="right")
                
                # Visual progress bar
                progress_frame = ctk.CTkFrame(app_frame, fg_color=self.colors['bg'], height=4)
                progress_frame.pack(fill="x", padx=15, pady=(0, 5))
                progress_frame.pack_propagate(False)
                
                progress_bar = ctk.CTkFrame(
                    progress_frame,
                    fg_color=self.colors['accent'],
                    height=4,
                    width=int((percentage / 100) * (app_frame.winfo_reqwidth() - 30))
                )
                progress_bar.pack(side="left", fill="y")
    
    def update_chart(self):
        """Update the weekly chart"""
        weekly_stats = self.db.get_weekly_stats()
        daily_stats = weekly_stats['daily_stats']
        
        # Clear and setup
        self.ax.clear()
        self.ax.set_facecolor(self.colors['card'])
        
        if not daily_stats:
            self.ax.text(0.5, 0.5, 'No data available yet', 
                        ha='center', va='center', 
                        transform=self.ax.transAxes,
                        color=self.colors['text_secondary'], fontsize=16)
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.canvas.draw()
            return
        
        # Prepare data
        dates = [datetime.fromisoformat(stat['date']) for stat in daily_stats]
        hours = [stat['total_seconds'] / 3600 for stat in daily_stats]
        
        # Styling
        self.ax.tick_params(colors=self.colors['text_secondary'], labelsize=10)
        for spine in self.ax.spines.values():
            spine.set_color(self.colors['text_secondary'])
            spine.set_alpha(0.3)
        
        # Create bar chart with gradient effect
        bars = self.ax.bar(dates, hours, width=0.6, color=self.colors['accent'], 
                          alpha=0.8, edgecolor=self.colors['accent'], linewidth=2)
        
        # Add value labels on bars
        for i, (date_val, hour_val) in enumerate(zip(dates, hours)):
            if hour_val > 0:
                self.ax.text(date_val, hour_val + 0.2, f'{hour_val:.1f}h',
                           ha='center', va='bottom', color=self.colors['text_primary'],
                           fontsize=9, weight='bold')
        
        self.ax.set_xlabel('Date', color=self.colors['text_primary'], fontsize=12, weight='bold')
        self.ax.set_ylabel('Hours', color=self.colors['text_primary'], fontsize=12, weight='bold')
        self.ax.set_title('Daily Screen Time (Last 7 Days)', 
                         color=self.colors['text_primary'], fontsize=14, weight='bold', pad=15)
        self.ax.grid(True, alpha=0.2, color=self.colors['text_secondary'], linestyle='--')
        
        # Format x-axis dates
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        self.fig.autofmt_xdate()
        
        # Set y-axis to start from 0
        self.ax.set_ylim(bottom=0)
        
        self.canvas.draw()
    
    def update_history_timeline(self):
        """Update the historical timeline"""
        # Clear existing widgets
        for widget in self.history_scroll.winfo_children():
            widget.destroy()
        
        # Get last 14 days
        historical_days = self.db.get_historical_days(days=14)
        
        if not historical_days:
            no_data_label = ctk.CTkLabel(
                self.history_scroll,
                text="No historical data available.",
                font=ctk.CTkFont(size=14),
                text_color=self.colors['text_secondary']
            )
            no_data_label.pack(pady=30)
            return
        
        # Create timeline items
        for day_data in historical_days:
            day_frame = ctk.CTkFrame(
                self.history_scroll,
                fg_color=self.colors['bg'],
                corner_radius=10
            )
            day_frame.pack(fill="x", padx=5, pady=5)
            
            # Make clickable
            day_frame.bind("<Button-1>", 
                          lambda e, d=day_data['date']: self.show_date_view(
                              datetime.fromisoformat(d).date()
                          ))
            for widget in [day_frame]:
                widget.bind("<Enter>", 
                           lambda e, w=day_frame: w.configure(fg_color='#1f2937'))
                widget.bind("<Leave>", 
                           lambda e, w=day_frame: w.configure(fg_color=self.colors['bg']))
            
            # Content
            content_frame = ctk.CTkFrame(day_frame, fg_color="transparent")
            content_frame.pack(fill="x", padx=15, pady=12)
            
            # Date label
            date_label = ctk.CTkLabel(
                content_frame,
                text=self.format_date_display(day_data['date']),
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=self.colors['text_primary'],
                anchor="w"
            )
            date_label.pack(side="left", fill="x", expand=True)
            
            # Time label
            time_label = ctk.CTkLabel(
                content_frame,
                text=self.format_time(day_data['total_seconds']),
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=self.colors['accent']
            )
            time_label.pack(side="right")
    
    def show_date_view(self, target_date):
        """Show detailed view for a specific date"""
        # Get stats for the date
        date_str = target_date.isoformat() if isinstance(target_date, date) else target_date
        stats = self.db.get_date_stats(date_str)
        
        # Create popup window
        popup = ctk.CTk()
        popup.title(f"Screen Time - {self.format_date_display(date_str)}")
        popup.geometry("800x600")
        popup.configure(fg_color=self.colors['bg'])
        
        # Header
        header = ctk.CTkLabel(
            popup,
            text=f"📅 {self.format_date_display(date_str)}",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors['text_primary']
        )
        header.pack(pady=20)
        
        # Total time
        total_label = ctk.CTkLabel(
            popup,
            text=f"Total: {self.format_time(stats['total_seconds'])}",
            font=ctk.CTkFont(size=20),
            text_color=self.colors['accent']
        )
        total_label.pack(pady=10)
        
        # Apps list
        apps_frame = ctk.CTkScrollableFrame(popup, fg_color=self.colors['card'], corner_radius=15)
        apps_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        if stats['top_apps']:
            total_time = sum(app['duration'] for app in stats['top_apps'])
            for i, app in enumerate(stats['top_apps'], 1):
                app_item = ctk.CTkFrame(apps_frame, fg_color=self.colors['bg'], corner_radius=8)
                app_item.pack(fill="x", padx=10, pady=5)
                
                # App info
                info_frame = ctk.CTkFrame(app_item, fg_color="transparent")
                info_frame.pack(fill="x", padx=15, pady=10)
                
                rank_label = ctk.CTkLabel(
                    info_frame,
                    text=f"#{i}",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=self.colors['accent'],
                    width=30
                )
                rank_label.pack(side="left")
                
                name_label = ctk.CTkLabel(
                    info_frame,
                    text=app['app_name'],
                    font=ctk.CTkFont(size=15, weight="bold"),
                    text_color=self.colors['text_primary'],
                    anchor="w"
                )
                name_label.pack(side="left", fill="x", expand=True, padx=10)
                
                time_label = ctk.CTkLabel(
                    info_frame,
                    text=self.format_time(app['duration']),
                    font=ctk.CTkFont(size=15, weight="bold"),
                    text_color=self.colors['text_primary']
                )
                time_label.pack(side="right")
                
                # Percentage
                if total_time > 0:
                    percentage = (app['duration'] / total_time) * 100
                    pct_label = ctk.CTkLabel(
                        info_frame,
                        text=f"{percentage:.1f}%",
                        font=ctk.CTkFont(size=12),
                        text_color=self.colors['text_secondary'],
                        width=60
                    )
                    pct_label.pack(side="right", padx=10)
        else:
            no_data = ctk.CTkLabel(
                apps_frame,
                text="No data for this date.",
                font=ctk.CTkFont(size=14),
                text_color=self.colors['text_secondary']
            )
            no_data.pack(pady=30)
        
        # Close button
        close_btn = ctk.CTkButton(
            popup,
            text="Close",
            command=popup.destroy,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=self.colors['accent']
        )
        close_btn.pack(pady=20)
        
        popup.mainloop()
    
    def toggle_pause(self):
        """Toggle pause/resume tracking"""
        if self.tracker_service.is_paused():
            self.tracker_service.resume()
            self.pause_button.configure(text="⏸ Pause Tracking")
            self.status_label.configure(text="● Tracking", text_color=self.colors['success'])
        else:
            self.tracker_service.pause()
            self.pause_button.configure(text="▶ Resume Tracking")
            self.status_label.configure(text="● Paused", text_color=self.colors['warning'])
    
    def update_loop(self):
        """Background thread to update display periodically"""
        while self.update_thread_running:
            time.sleep(5)  # Update every 5 seconds
            if self.root.winfo_exists() and self.root.winfo_viewable():
                try:
                    self.root.after(0, self.refresh_data)
                except:
                    pass
    
    def show_window(self):
        """Show the window"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.refresh_data()
    
    def hide_window(self):
        """Hide the window (minimize to tray)"""
        self.root.withdraw()
    
    def destroy(self):
        """Clean up on exit"""
        self.update_thread_running = False
        self.root.destroy()
