import pcbnew
import os
import json
import wx

from .dialog import RoundedRectDialog

def rm_edge_cuts(board):
    """Safely removes all items on the Edge.Cuts layer."""
    for drawing in list(board.GetDrawings()):
        if drawing.GetLayer() == pcbnew.Edge_Cuts:
            board.Remove(drawing)

class RoundedRectOutlinePlugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Rounded Rectangle Outline"
        self.category = "Modify PCB"
        self.description = "Generates a rounded rectangle board outline on the Edge.Cuts layer"
        self.show_toolbar_button = True
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        if os.path.exists(icon_path):
            self.icon_file_name = icon_path

    def Run(self):
        board = pcbnew.GetBoard()
        
        # Load config to remember last used values
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        config = {
            "width": 100.0,
            "height": 50.0,
            "radius":  5.0,
            "replace": True,
            "use_custom_pos": False,
            "pos_x": 0.0,
            "pos_y": 0.0
        }
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config.update(json.load(f))
            except Exception:
                pass

        dlg = RoundedRectDialog(None, config)
        if dlg.ShowModal() == wx.ID_OK:
            params = dlg.get_params()
            
            # Save config for next time
            try:
                with open(config_path, 'w') as f:
                    json.dump(params, f)
            except Exception:
                pass
                
            width = params["width"]
            height = params["height"]
            radius = params["radius"]
            replace = params["replace"]
            use_custom_pos = params["use_custom_pos"]
            pos_x = params["pos_x"]
            pos_y = params["pos_y"]
            
            if replace:
                rm_edge_cuts(board)
            
            if use_custom_pos:
                cx_mm, cy_mm = pos_x, pos_y
            else:
                # Default to placing it at the board's page center
                try:
                    page_info = board.GetPageSettings()
                    size_x_iu = page_info.GetSizeIU().x
                    size_y_iu = page_info.GetSizeIU().y
                    cx_mm = pcbnew.ToMM(size_x_iu / 2.0)
                    cy_mm = pcbnew.ToMM(size_y_iu / 2.0)
                except Exception:
                    # Fallback for KiCad v9+ where GetPageSettings might not have GetSizeIU
                    # Default A4 page size
                    cx_mm = 297.0 / 2.0
                    cy_mm = 210.0 / 2.0
                
            self.generate_outline(board, width, height, radius, cx_mm, cy_mm)
            
            pcbnew.Refresh()

    def add_line(self, board, x1, y1, x2, y2):
        line = pcbnew.PCB_SHAPE(board)
        line.SetShape(pcbnew.SHAPE_T_SEGMENT)
        line.SetLayer(pcbnew.Edge_Cuts)
        line.SetWidth(pcbnew.FromMM(0.1))
        # Ensure we convert accurately to integer internal units
        line.SetStart(pcbnew.VECTOR2I(int(x1), int(y1)))
        line.SetEnd(pcbnew.VECTOR2I(int(x2), int(y2)))
        board.Add(line)

    def add_arc(self, board, cx, cy, sx, sy, angle_deg):
        arc = pcbnew.PCB_SHAPE(board)
        arc.SetShape(pcbnew.SHAPE_T_ARC)
        arc.SetLayer(pcbnew.Edge_Cuts)
        arc.SetWidth(pcbnew.FromMM(0.1))
        
        arc.SetCenter(pcbnew.VECTOR2I(int(cx), int(cy)))
        arc.SetStart(pcbnew.VECTOR2I(int(sx), int(sy)))
        
        # KiCad API compatibility for arc angles
        if hasattr(pcbnew, 'EDA_ANGLE'):
            # KiCad 7 and 8 API
            angle = pcbnew.EDA_ANGLE(angle_deg, pcbnew.DEGREES_T)
            arc.SetArcAngleAndEnd(angle)
        else:
            # KiCad 6 and earlier fallback
            arc.SetArcAngleAndEnd(int(angle_deg * 10))
            
        board.Add(arc)

    def generate_outline(self, board, w_mm, h_mm, r_mm, cx_mm, cy_mm):
        # Convert all mm values to Internal Units (IU)
        W = pcbnew.FromMM(w_mm)
        H = pcbnew.FromMM(h_mm)
        R = pcbnew.FromMM(r_mm)
        cx = pcbnew.FromMM(cx_mm)
        cy = pcbnew.FromMM(cy_mm)
        
        # 1. Draw the 4 straight edge segments
        
        # Top edge
        if W > 2*R:
            self.add_line(board, cx - W/2 + R, cy - H/2, cx + W/2 - R, cy - H/2)
            
        # Right edge
        if H > 2*R:
            self.add_line(board, cx + W/2, cy - H/2 + R, cx + W/2, cy + H/2 - R)
            
        # Bottom edge
        if W > 2*R:
            self.add_line(board, cx + W/2 - R, cy + H/2, cx - W/2 + R, cy + H/2)
            
        # Left edge
        if H > 2*R:
            self.add_line(board, cx - W/2, cy + H/2 - R, cx - W/2, cy - H/2 + R)

        # 2. Draw the 4 rounded corner arcs (if R > 0)
        
        if R > 0:
            # Positive angle (90) rotates the arc clockwise on KiCad's screen since Y goes down
            
            # Top-Right corner arc
            self.add_arc(board, 
                         cx + W/2 - R, cy - H/2 + R, # Center
                         cx + W/2 - R, cy - H/2,     # Start (tangent to top edge)
                         90)
                         
            # Bottom-Right corner arc
            self.add_arc(board, 
                         cx + W/2 - R, cy + H/2 - R, # Center
                         cx + W/2, cy + H/2 - R,     # Start (tangent to right edge)
                         90)
                         
            # Bottom-Left corner arc
            self.add_arc(board, 
                         cx - W/2 + R, cy + H/2 - R, # Center
                         cx - W/2 + R, cy + H/2,     # Start (tangent to bottom edge)
                         90)
                         
            # Top-Left corner arc
            self.add_arc(board, 
                         cx - W/2 + R, cy - H/2 + R, # Center
                         cx - W/2, cy - H/2 + R,     # Start (tangent to left edge)
                         90)
