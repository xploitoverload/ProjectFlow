# app/utils/pagination.py
"""
Pagination utilities for list views.
"""

from flask import request, url_for
from math import ceil


class Paginator:
    """Handle pagination for list views."""
    
    def __init__(self, query, page=None, per_page=25, total_pages_display=7):
        """
        Initialize paginator.
        
        Args:
            query: SQLAlchemy query object
            page: Current page number (default: 1 from request args)
            per_page: Items per page (default: 25)
            total_pages_display: Number of page numbers to display
        """
        self.query = query
        self.per_page = per_page
        self.total_pages_display = total_pages_display
        
        # Get page from request args or parameter
        if page is None:
            page = request.args.get('page', 1, type=int)
        
        self.page = max(1, page)
        self.total_items = query.count()
        self.total_pages = ceil(self.total_items / self.per_page) if self.total_items > 0 else 1
        
        # Validate current page
        if self.page > self.total_pages:
            self.page = self.total_pages
    
    @property
    def items(self):
        """Get items for current page."""
        offset = (self.page - 1) * self.per_page
        return self.query.offset(offset).limit(self.per_page).all()
    
    @property
    def has_prev(self):
        """Check if previous page exists."""
        return self.page > 1
    
    @property
    def has_next(self):
        """Check if next page exists."""
        return self.page < self.total_pages
    
    @property
    def prev_page(self):
        """Get previous page number."""
        return self.page - 1 if self.has_prev else None
    
    @property
    def next_page(self):
        """Get next page number."""
        return self.page + 1 if self.has_next else None
    
    @property
    def pages(self):
        """Get list of page numbers to display."""
        # Calculate start and end pages for display
        if self.total_pages <= self.total_pages_display:
            start_page = 1
            end_page = self.total_pages
        else:
            half = self.total_pages_display // 2
            if self.page <= half:
                start_page = 1
                end_page = self.total_pages_display
            elif self.page >= self.total_pages - half:
                start_page = self.total_pages - self.total_pages_display + 1
                end_page = self.total_pages
            else:
                start_page = self.page - half
                end_page = self.page + half
        
        return list(range(start_page, end_page + 1))
    
    def get_page_url(self, page_num):
        """Get URL for specific page."""
        # Get current request parameters
        params = request.args.to_dict()
        params['page'] = page_num
        
        return url_for(request.endpoint, **params)
    
    def get_prev_url(self):
        """Get URL for previous page."""
        if self.has_prev:
            return self.get_page_url(self.prev_page)
        return None
    
    def get_next_url(self):
        """Get URL for next page."""
        if self.has_next:
            return self.get_page_url(self.next_page)
        return None
    
    @property
    def start_item(self):
        """Get number of first item on current page."""
        return (self.page - 1) * self.per_page + 1 if self.total_items > 0 else 0
    
    @property
    def end_item(self):
        """Get number of last item on current page."""
        end = self.page * self.per_page
        return min(end, self.total_items)
    
    def __iter__(self):
        """Make paginator iterable."""
        return iter(self.items)
    
    def __len__(self):
        """Get length of items on current page."""
        return len(self.items)


class PaginationConfig:
    """Configuration for pagination."""
    
    DEFAULT_PER_PAGE = 25
    PER_PAGE_OPTIONS = [10, 25, 50, 100]
    MAX_PER_PAGE = 500
    
    @staticmethod
    def get_per_page(requested_per_page=None):
        """Get safe per_page value."""
        if requested_per_page is None:
            requested_per_page = request.args.get('per_page', PaginationConfig.DEFAULT_PER_PAGE, type=int)
        
        # Ensure value is within allowed range
        if requested_per_page not in PaginationConfig.PER_PAGE_OPTIONS:
            if requested_per_page > PaginationConfig.MAX_PER_PAGE:
                requested_per_page = PaginationConfig.MAX_PER_PAGE
            elif requested_per_page < 1:
                requested_per_page = PaginationConfig.DEFAULT_PER_PAGE
        
        return requested_per_page


# Helper function for template use
def paginate(query, page=None, per_page=None):
    """Create and return paginator object."""
    if per_page is None:
        per_page = PaginationConfig.get_per_page()
    
    return Paginator(query, page, per_page)
