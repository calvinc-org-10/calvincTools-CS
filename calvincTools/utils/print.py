"""
Printing utilities for Qt widgets.
"""

from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPainter, QRegion, QImage
from PySide6.QtWidgets import QWidget, QScrollArea, QFileDialog
from PySide6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog


class cPrintManager:
    """
    Printing manager for long QWidgets that may span multiple pages.
    Supports both print preview and PDF export.
    
    Usage:
        # Initialize manager and show preview
        manager = cPrintManager(widget)
        manager.open_preview()
        
        # Or export directly to PDF
        manager.export_pdf()
    """
    
    def __init__(self, target_widget: QWidget):
        """
        Initialize the print manager.
        
        Args:
            target_widget: The widget to print. Can be a QScrollArea or any QWidget.
        """
        # Determine if we are dealing with a ScrollArea
        if isinstance(target_widget, QScrollArea):
            self.source = target_widget.widget()
        else:
            self.source = target_widget
    # __init__

    def open_preview(self):
        """Opens the interactive preview window."""
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        preview = QPrintPreviewDialog(printer, self.source)
        preview.paintRequested.connect(self.handle_print)
        preview.exec()
    # open_preview

    def export_pdf(self):
        """Directly exports the widget to a PDF file without a dialog."""
        file_path, _ = QFileDialog.getSaveFileName(
            self.source, "Export PDF", "", "PDF Files (*.pdf)"
        )
        
        if file_path:
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_path)
            self.handle_print(printer)
    # export_pdf

    def handle_print(self, printer: QPrinter):
        """
        Render widget to printer via QImage intermediate.
        
        Args:
            printer: QPrinter object configured for the output.
        """
        if not self.source:
            print("No target widget to print")
            return

        self.source.adjustSize()
        page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
        widget_rect = self.source.rect()
        
        scale = page_rect.width() / widget_rect.width()
        scaled_page_height = page_rect.height() / scale
        total_height = widget_rect.height()
        current_y = 0
        page_num = 0
        
        painter = QPainter()
        if not painter.begin(printer):
            print("Could not start painter")
            return

        try:
            while current_y < total_height:
                page_num += 1
                
                # Render this page's slice to a QImage
                clip_height = min(int(scaled_page_height), int(total_height - current_y))
                page_image = QImage(
                    int(widget_rect.width()), 
                    clip_height, 
                    QImage.Format.Format_ARGB32
                )
                page_image.fill(Qt.GlobalColor.white)
                
                # Paint the widget slice onto the image
                img_painter = QPainter(page_image)
                img_painter.translate(0, -int(current_y))
                self.source.render(img_painter, QPoint(0, 0))
                img_painter.end()
                
                # Scale and paint the image to the printer
                painter.scale(scale, scale)
                painter.drawImage(0, 0, page_image)
                painter.resetTransform()
                
                current_y += scaled_page_height
                
                if current_y < total_height:
                    if not printer.newPage():
                        print("New page failed")
                        break
            # while
        finally:
            painter.end()
        # end try
    # handle_print
# cPrintManager
