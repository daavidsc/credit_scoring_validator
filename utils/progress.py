# utils/progress.py

"""
Progress tracking utilities for analysis modules
"""

class ProgressTracker:
    """Tracks progress within an allocated range"""
    
    def __init__(self, analysis_status=None, start_progress=0, progress_span=100):
        self.analysis_status = analysis_status
        self.start_progress = start_progress
        self.progress_span = progress_span
    
    def update(self, relative_progress, message=""):
        """Update progress with a value between 0.0 and 1.0 relative to allocated range"""
        if self.analysis_status:
            absolute_progress = self.start_progress + int(relative_progress * self.progress_span)
            self.analysis_status["progress"] = absolute_progress
            if message:
                self.analysis_status["message"] = message
    
    def set_status_reference(self, status_ref, start_progress=0, progress_span=100):
        """Set reference to global analysis status and progress range"""
        self.analysis_status = status_ref
        self.start_progress = start_progress
        self.progress_span = progress_span

# Global progress trackers for each analysis module
bias_progress = ProgressTracker()
robustness_progress = ProgressTracker()
consistency_progress = ProgressTracker()
accuracy_progress = ProgressTracker()
