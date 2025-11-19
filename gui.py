"""
GUI Dashboard for Screen Time Tracker
Modern interface using customtkinter
"""
import customtkinter as ctk
import threading
import time
from datetime import datetime, timedelta
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates


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
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Initially hide window (show via tray icon)
        self.root.withdraw()
        
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
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        header = ctk.CTkLabel(
            main_frame,
            text="Screen Time Tracker",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        header.pack(pady=(10, 20))
        
        # Today's stats frame
        today_frame = ctk.CTkFrame(main_frame)
        today_frame.pack(fill="x", padx=10, pady=5)
        
        today_label = ctk.CTkLabel(
            today_frame,
            text="Today",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        today_label.pack(pady=10)
        
        # Total time display
        self.total_time_label = ctk.CTkLabel(
            today_frame,
            text="0h 0m",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#4a9eff"
        )
        self.total_time_label.pack(pady=5)
        
        # Top apps frame
        apps_frame = ctk.CTkFrame(main_frame)
        apps_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        apps_label = ctk.CTkLabel(
            apps_frame,
            text="Top Applications",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        apps_label.pack(pady=10)
        
        # Scrollable frame for apps
        self.apps_scroll = ctk.CTkScrollableFrame(apps_frame, height=200)
        self.apps_scroll.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Chart frame
        chart_frame = ctk.CTkFrame(main_frame)
        chart_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        chart_label = ctk.CTkLabel(
            chart_frame,
            text="Weekly Overview",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        chart_label.pack(pady=10)
        
        # Matplotlib figure
        self.fig = Figure(figsize=(8, 4), facecolor='#1a1a1a')
        self.ax = self.fig.add_subplot(111, facecolor='#1a1a1a')
        self.ax.tick_params(colors='white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['right'].set_color('white')
        
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)
        
        # Control buttons frame
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        # Pause/Resume button
        self.pause_button = ctk.CTkButton(
            controls_frame,
            text="Pause Tracking",
            command=self.toggle_pause,
            width=150
        )
        self.pause_button.pack(side="left", padx=5)
        
        # Refresh button
        refresh_button = ctk.CTkButton(
            controls_frame,
            text="Refresh",
            command=self.refresh_data,
            width=150
        )
        refresh_button.pack(side="left", padx=5)
        
        # Hide button
        hide_button = ctk.CTkButton(
            controls_frame,
            text="Hide to Tray",
            command=self.hide_window,
            width=150
        )
        hide_button.pack(side="right", padx=5)
        
        # Initial data load
        self.refresh_data()
    
    def format_time(self, seconds):
        """Format seconds into readable time string"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def refresh_data(self):
        """Refresh all displayed data"""
        # Get today's stats
        today_stats = self.db.get_today_stats()
        total_seconds = today_stats['total_seconds']
        self.total_time_label.configure(text=self.format_time(total_seconds))
        
        # Update top apps
        self.update_apps_list(today_stats['top_apps'])
        
        # Update chart
        self.update_chart()
        
        # Update pause button
        if self.tracker_service.is_paused():
            self.pause_button.configure(text="Resume Tracking")
        else:
            self.pause_button.configure(text="Pause Tracking")
    
    def update_apps_list(self, top_apps):
        """Update the top applications list"""
        # Clear existing widgets
        for widget in self.apps_scroll.winfo_children():
            widget.destroy()
        
        if not top_apps:
            no_data_label = ctk.CTkLabel(
                self.apps_scroll,
                text="No data yet. Start using applications to see statistics.",
                font=ctk.CTkFont(size=12)
            )
            no_data_label.pack(pady=20)
            return
        
        # Create app items
        for i, app in enumerate(top_apps[:10], 1):
            app_frame = ctk.CTkFrame(self.apps_scroll)
            app_frame.pack(fill="x", padx=5, pady=2)
            
            # Rank
            rank_label = ctk.CTkLabel(
                app_frame,
                text=f"#{i}",
                font=ctk.CTkFont(size=14, weight="bold"),
                width=40
            )
            rank_label.pack(side="left", padx=5)
            
            # App name
            name_label = ctk.CTkLabel(
                app_frame,
                text=app['app_name'],
                font=ctk.CTkFont(size=14),
                anchor="w"
            )
            name_label.pack(side="left", padx=10, fill="x", expand=True)
            
            # Duration
            duration_label = ctk.CTkLabel(
                app_frame,
                text=self.format_time(app['duration']),
                font=ctk.CTkFont(size=14),
                width=80
            )
            duration_label.pack(side="right", padx=5)
    
    def update_chart(self):
        """Update the weekly chart"""
        weekly_stats = self.db.get_weekly_stats()
        daily_stats = weekly_stats['daily_stats']
        
        if not daily_stats:
            self.ax.clear()
            self.ax.text(0.5, 0.5, 'No data available', 
                        ha='center', va='center', 
                        transform=self.ax.transAxes,
                        color='white', fontsize=14)
            self.canvas.draw()
            return
        
        # Prepare data
        dates = [datetime.fromisoformat(stat['date']) for stat in daily_stats]
        hours = [stat['total_seconds'] / 3600 for stat in daily_stats]
        
        # Clear and redraw
        self.ax.clear()
        self.ax.set_facecolor('#1a1a1a')
        self.ax.tick_params(colors='white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['right'].set_color('white')
        
        # Plot
        self.ax.plot(dates, hours, marker='o', linewidth=2, markersize=6, color='#4a9eff')
        self.ax.fill_between(dates, hours, alpha=0.3, color='#4a9eff')
        self.ax.set_xlabel('Date', color='white')
        self.ax.set_ylabel('Hours', color='white')
        self.ax.set_title('Daily Screen Time (Last 7 Days)', color='white', fontsize=12)
        self.ax.grid(True, alpha=0.3, color='gray')
        
        # Format x-axis dates
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        self.ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        self.fig.autofmt_xdate()
        
        self.canvas.draw()
    
    def toggle_pause(self):
        """Toggle pause/resume tracking"""
        if self.tracker_service.is_paused():
            self.tracker_service.resume()
            self.pause_button.configure(text="Pause Tracking")
        else:
            self.tracker_service.pause()
            self.pause_button.configure(text="Resume Tracking")
    
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

