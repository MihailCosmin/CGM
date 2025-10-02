"""
Clear Text CGM Writer
Writes CGM commands in clear text format according to ISO/IEC 8632-4:1999 specification
"""
from typing import List, TextIO
from cgm_classes import Message
from cgm_enums import Severity


class ClearTextWriter:
    """Writes CGM commands in clear text format"""
    
    LINE_FEED = "\n"
    MAX_CHARS_PER_LINE = 80
    
    def __init__(self, stream: TextIO):
        self.stream = stream
        self.messages: List[Message] = []
        self.current_command = None
        self.current_chars_per_line = 0
    
    def write_line(self, line: str):
        """Write a line of text"""
        self.write(line)
        self.write(self.LINE_FEED)
        self.current_chars_per_line = 0
    
    def write(self, text: str):
        """Write text with automatic line wrapping"""
        if not text:
            return
        
        if self.LINE_FEED in text and len(text) > 1:
            self._write_line_feeds(text)
        else:
            if self.current_chars_per_line + len(text) > self.MAX_CHARS_PER_LINE:
                if text in (self.LINE_FEED, ";") or len(text) == 1:
                    self.stream.write(text)
                else:
                    self._write_split_text(text)
            else:
                self.stream.write(text)
                self.current_chars_per_line += len(text)
    
    def _write_split_text(self, text: str):
        """Split and write text across multiple lines"""
        while self.current_chars_per_line + len(text) > self.MAX_CHARS_PER_LINE and text:
            # Find last separator before line limit
            max_pos = self.MAX_CHARS_PER_LINE - self.current_chars_per_line
            next_separator = text.rfind(" ", 0, max_pos)
            
            # Don't split after command name before string parameter
            if next_separator > 0 and next_separator + 1 < len(text) and text[next_separator + 1] == "'":
                next_separator = -1
            
            if next_separator == -1:
                next_separator = text.rfind(self.LINE_FEED, 0, max_pos)
            
            if next_separator == -1:
                next_separator = text.find(" ")
            
            if next_separator == -1:
                next_separator = text.find(self.LINE_FEED)
            
            if next_separator > 0:
                current_line = text[:next_separator]
                text = text[next_separator:]
                self.write_line(current_line)
            else:
                self.stream.write(text)
                self.current_chars_per_line = 0
                text = ""
        
        # Write remaining text
        self.write(text)
    
    def _write_line_feeds(self, text: str):
        """Write text containing line feeds"""
        lines = text.split(self.LINE_FEED)
        for i in range(len(lines) - 1):
            self.write_line(lines[i])
        self.write(lines[-1])
    
    def write_command(self, command):
        """Write a CGM command"""
        self.current_command = command
        command.write_as_clear_text(self)
        self.current_command = None
    
    def info(self, message: str):
        """Log an info message"""
        if self.current_command:
            self.messages.append(Message(
                Severity.INFO.value,
                self.current_command.element_class,
                self.current_command.element_id,
                message,
                str(self.current_command)
            ))
        else:
            self.messages.append(Message(
                Severity.INFO.value,
                0,
                0,
                message,
                ""
            ))
