import wx

class PreviewPanel(wx.Panel):
    """ A simple panel that live-draws a preview of the rounded rectangle """
    def __init__(self, parent, dialog):
        super().__init__(parent, size=(180, 180))
        self.dialog = dialog
        self.Bind(wx.EVT_PAINT, self.on_paint)
        # Check system theme colors for better visibility
        is_dark = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW).GetLuminance() < 0.5
        bg_col = wx.Colour(40, 40, 40) if is_dark else wx.Colour(240, 240, 240)
        line_col = wx.Colour(255, 200, 0) if is_dark else wx.Colour(20, 100, 200)
        
        self.SetBackgroundColour(bg_col)
        self.pen = wx.Pen(line_col, 2)

    def on_paint(self, event):
        dc = wx.PaintDC(self)
        dc.Clear()
        
        try:
            w = float(self.dialog.width_ctrl.GetValue())
            h = float(self.dialog.height_ctrl.GetValue())
            r = float(self.dialog.radius_ctrl.GetValue())
            angle = float(self.dialog.angle_ctrl.GetValue())
        except ValueError:
            return
            
        if w <= 0 or h <= 0 or r < 0:
            return
            
        # Clamp preview radius
        r = min(r, min(w, h)/2.0)
        
        max_dim = max(w, h)
        if max_dim <= 0: return
        
        # Scale shape to fit inside our 180x180 panel comfortably
        target_size = 140.0
        scale = target_size / max_dim
        
        draw_w = w * scale
        draw_h = h * scale
        draw_r = r * scale
        
        cx, cy = 90, 90  # Center of the panel
        
        dc.SetPen(self.pen)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        
        # Use GraphicsContext for rotation capability
        gc = wx.GraphicsContext.Create(dc)
        if gc:
            gc.SetPen(self.pen)
            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.Translate(cx, cy)
            import math
            gc.Rotate(math.radians(-angle)) # Negative because KiCad Y goes down, but preview should feel intuitive
            
            # Draw the rounded rectangle centered at 0,0 locally
            gc.DrawRoundedRectangle(-draw_w/2, -draw_h/2, draw_w, draw_h, draw_r)
        else:
            # Fallback if GraphicsContext fails
            dc.DrawRoundedRectangle(int(cx - draw_w/2), int(cy - draw_h/2), int(draw_w), int(draw_h), int(draw_r))


class RoundedRectDialog(wx.Dialog):
    def __init__(self, parent, config):
        super().__init__(parent, title="Rounded Rectangle Generator", style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.config = config
        
        # Main horizontally split sizer
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Left side containing inputs and checkboxes
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        
        grid = wx.FlexGridSizer(4, 2, 10, 10)
        grid.AddGrowableCol(1)
        
        self.width_ctrl = self._add_input(grid, "Width (mm):", str(config.get("width", 100.0)))
        self.height_ctrl = self._add_input(grid, "Height (mm):", str(config.get("height", 50.0)))
        self.radius_ctrl = self._add_input(grid, "Radius (mm):", str(config.get("radius", 5.0)))
        self.angle_ctrl = self._add_input(grid, "Angle (deg):", str(config.get("angle", 0.0)))
        
        # Bind events for live preview updates
        self.width_ctrl.Bind(wx.EVT_TEXT, self.on_text_change)
        self.height_ctrl.Bind(wx.EVT_TEXT, self.on_text_change)
        self.radius_ctrl.Bind(wx.EVT_TEXT, self.on_text_change)
        self.angle_ctrl.Bind(wx.EVT_TEXT, self.on_text_change)
        
        left_sizer.Add(grid, flag=wx.ALL | wx.EXPAND, border=10)
        
        # Checkboxes
        self.replace_cb = wx.CheckBox(self, label="Replace existing Edge.Cuts")
        self.replace_cb.SetValue(config.get("replace", True))
        left_sizer.Add(self.replace_cb, flag=wx.ALL, border=10)
        
        self.custom_pos_cb = wx.CheckBox(self, label="Place at specific X/Y position")
        self.custom_pos_cb.SetValue(config.get("use_custom_pos", False))
        self.custom_pos_cb.Bind(wx.EVT_CHECKBOX, self.on_custom_pos_toggle)
        left_sizer.Add(self.custom_pos_cb, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
        
        # Custom Position Inputs
        self.pos_grid = wx.FlexGridSizer(2, 2, 5, 5)
        self.pos_grid.AddGrowableCol(1)
        self.pos_x_ctrl = self._add_input(self.pos_grid, "Center X (mm):", str(config.get("pos_x", 0.0)))
        self.pos_y_ctrl = self._add_input(self.pos_grid, "Center Y (mm):", str(config.get("pos_y", 0.0)))
        
        left_sizer.Add(self.pos_grid, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, border=10)
        
        self.on_custom_pos_toggle(None) # Set initial enable/disable state
        
        # Bottom action buttons
        btn_sizer = wx.StdDialogButtonSizer()
        
        ok_btn = wx.Button(self, wx.ID_OK)
        ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)
        btn_sizer.AddButton(ok_btn)
        
        cancel_btn = wx.Button(self, wx.ID_CANCEL)
        btn_sizer.AddButton(cancel_btn)
        
        btn_sizer.Realize()
        left_sizer.Add(btn_sizer, flag=wx.EXPAND | wx.ALL, border=10)
        
        top_sizer.Add(left_sizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        
        # Right side preview panel
        self.preview = PreviewPanel(self, self)
        top_sizer.Add(self.preview, proportion=0, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=10)
        
        self.SetSizer(top_sizer)
        self.Layout()
        self.Fit()
        
    def _add_input(self, sizer, label_text, default_val):
        label = wx.StaticText(self, label=label_text)
        ctrl = wx.TextCtrl(self, value=default_val)
        sizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(ctrl, flag=wx.EXPAND)
        return ctrl
        
    def on_text_change(self, event):
        self.preview.Refresh()
        event.Skip()

    def on_custom_pos_toggle(self, event):
        enabled = self.custom_pos_cb.GetValue()
        self.pos_x_ctrl.Enable(enabled)
        self.pos_y_ctrl.Enable(enabled)
        if event:
            event.Skip()

    def get_params(self):
        try:
            w = float(self.width_ctrl.GetValue())
            h = float(self.height_ctrl.GetValue())
            r = float(self.radius_ctrl.GetValue())
            a = float(self.angle_ctrl.GetValue())
        except ValueError:
            w, h, r, a = 100.0, 50.0, 5.0, 0.0
            
        try:
            px = float(self.pos_x_ctrl.GetValue())
            py = float(self.pos_y_ctrl.GetValue())
        except ValueError:
            px, py = 0.0, 0.0
            
        r = min(r, min(w, h)/2.0)
            
        return {
            "width": w,
            "height": h,
            "radius": r,
            "angle": a,
            "replace": self.replace_cb.GetValue(),
            "use_custom_pos": self.custom_pos_cb.GetValue(),
            "pos_x": px,
            "pos_y": py
        }

    def on_ok(self, event):
        try:
            w = float(self.width_ctrl.GetValue())
            h = float(self.height_ctrl.GetValue())
            r = float(self.radius_ctrl.GetValue())
            a = float(self.angle_ctrl.GetValue())
        except ValueError:
            wx.MessageBox("Please enter valid numbers for Width, Height, Radius, and Angle.", "Invalid Input", wx.OK | wx.ICON_ERROR)
            return

        if self.custom_pos_cb.GetValue():
            try:
                float(self.pos_x_ctrl.GetValue())
                float(self.pos_y_ctrl.GetValue())
            except ValueError:
                wx.MessageBox("Please enter valid numbers for X and Y positions.", "Invalid Input", wx.OK | wx.ICON_ERROR)
                return
            
        if w <= 0 or h <= 0:
            wx.MessageBox("Width and Height must be greater than 0.", "Invalid Input", wx.OK | wx.ICON_ERROR)
            return
            
        if r < 0:
            wx.MessageBox("Radius cannot be negative.", "Invalid Input", wx.OK | wx.ICON_ERROR)
            return
            
        # Hard cap the radius so it never exceeds half the shortest side
        max_r = min(w, h) / 2.0
        if r > max_r:
            self.radius_ctrl.SetValue(f"{max_r:.2f}")
            wx.MessageBox(f"Radius was automatically clamped to {max_r:.2f} mm\n(It cannot exceed half the shortest side).", "Info", wx.OK | wx.ICON_INFORMATION)
            self.preview.Refresh()
            return
            
        event.Skip()
