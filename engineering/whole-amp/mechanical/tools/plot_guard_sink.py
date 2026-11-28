"""Render the reviewed sink, package, guard and cabinet sections."""


def draw(OUT_SVG, result, section, cabinet):
    SINK, PKG, ASSUME = result['sink_mm'], result['package_mm'], result['assumptions']
    envelope = result['envelopes_mm']
    env_bare = envelope['bare_max_w_d_h']
    env_guard = envelope['guarded_free_standing_w_d_h']
    flat_bare, flat_guard = envelope['flat_on_wall_protrusion_bare'], envelope['flat_on_wall_protrusion_guarded']
    chan_depth, stack = section['channel_depth'], section['stack']
    r_w, pkg_len, lead_span, G = section['washer_radius'], section['land_length'], section['lead_span'], section['guard_gap']
    frame_w, frame_d = cabinet['frame']
    controls_w, controls_d = cabinet['controls']
    end_w, R, corner = cabinet['end_width'], cabinet['corner_radius'], cabinet['corner_error']
    x0, y0 = cabinet['origin']
    depth_avail, width_avail = cabinet['depth'], cabinet['width']
    # ------------------------------------------------ dimensioned SVG (1 mm = 4 px)
    S = 4


    def rect(x, y, w, h, style):
        return '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" %s/>' % (x * S, y * S, w * S, h * S, style)


    def text(x, y, s, size=11, anchor='start'):
        return '<text x="%.1f" y="%.1f" font-size="%d" text-anchor="%s">%s</text>' % (x * S, y * S, size, anchor, s)


    def dim(x1, y1, x2, y2, label):
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#06c" stroke-width="1"/>'
                % (x1 * S, y1 * S, x2 * S, y2 * S)) + \
            '<text x="%.1f" y="%.1f" font-size="10" fill="#06c" text-anchor="middle">%s</text>' % (mx * S, my * S - 3, label)


    OUTL = 'fill="#ddd" stroke="#000" stroke-width="1"'
    GRD = 'fill="none" stroke="#c00" stroke-width="1" stroke-dasharray="6 3"'
    PK = 'fill="#fc6" stroke="#000" stroke-width="1"'
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="760" font-family="Helvetica,Arial,sans-serif">',
             '<rect width="1180" height="760" fill="#fff"/>',
             text(5, 6, 'CB-008 guard-sink fit screen: Boyd 530002B02500G + Apex PA340CC. Nominal catalog dimensions, mm. '
                        'Screen only, not a fit release.', 13)]

    # View 1: front elevation (device side)
    ox, oy = 25, 22
    parts += [text(ox - 10, oy - 10, 'VIEW 1 front: channel, single screw hole, package above hole', 12),
              rect(ox - G, oy - G, SINK['width'] + 2 * G, SINK['height_A'] + G, GRD),
              rect(ox, oy, SINK['width'], SINK['height_A'], OUTL),
              rect(ox + (SINK['width'] - SINK['channel_width']) / 2, oy, SINK['channel_width'], SINK['height_A'],
                   'fill="#f4f4f4" stroke="#666" stroke-width="1"')]
    hx, hy = ox + SINK['hole_x_from_edge'], oy + SINK['height_A'] - SINK['hole_B_from_base']
    parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#fff" stroke="#000"/>' % (hx * S, hy * S, SINK['hole_C_dia'] / 2 * S))
    py = hy - r_w - pkg_len
    parts += [rect(hx - PKG['land_tab_w'] / 2, py, PKG['land_tab_w'], PKG['land_tab_l'], PK),
              rect(hx - lead_span / 2, py + PKG['land_tab_l'] + PKG['land_gap'], lead_span, PKG['land_lead_l'], PK),
              dim(ox, oy + SINK['height_A'] + 5, ox + SINK['width'], oy + SINK['height_A'] + 5, '41.91'),
              dim(ox - 11, oy, ox - 11, oy + SINK['height_A'], '63.50'),
              dim(ox + SINK['width'] + 3, hy, ox + SINK['width'] + 3, oy + SINK['height_A'], '18.29'),
              text(ox + SINK['width'] + 9, py + 6, 'land 13.0 x 18.64', 10),
              text(ox + SINK['width'] + 9, py + 10, 'in 17.02 channel', 10),
              text(ox - G, oy + SINK['height_A'] + 11, 'red dashed = guard, %.1f gap + %.1f metal (assumed)'
                   % (ASSUME['guard_air_gap_mm'], ASSUME['guard_material_mm']), 10)]

    # View 2: section (plan)
    ox2, oy2 = 120, 30
    parts += [text(ox2 - 8, oy - 6, 'VIEW 2 section: web, channel depth, stack', 12),
              rect(ox2 - G, oy2 - G, SINK['width'] + 2 * G, SINK['depth'] + 2 * G, GRD),
              rect(ox2, oy2, SINK['width'], SINK['depth'], 'fill="#eee" stroke="#999" stroke-width="1" stroke-dasharray="2 2"'),
              rect(ox2, oy2 + (SINK['depth'] - SINK['web_thickness']) / 2, SINK['width'], SINK['web_thickness'], OUTL)]
    cx = ox2 + (SINK['width'] - SINK['channel_width']) / 2
    wy = oy2 + (SINK['depth'] + SINK['web_thickness']) / 2
    parts += [rect(cx + 0.5, wy + ASSUME['interface_mm'], 16.0, ASSUME['carrier_pcb_mm'], 'fill="#3a3" stroke="#000"'),
              rect(cx + (SINK['channel_width'] - PKG['body_width_max']) / 2, wy + ASSUME['interface_mm'] + ASSUME['carrier_pcb_mm'],
                   PKG['body_width_max'], PKG['thickness_max'], PK),
              dim(ox2, oy2 + SINK['depth'] + G + 4, ox2 + SINK['width'], oy2 + SINK['depth'] + G + 4, '41.91'),
              dim(ox2 - G - 3, oy2, ox2 - G - 3, oy2 + SINK['depth'], '25.40'),
              text(ox2, oy2 + SINK['depth'] + G + 10, 'channel depth %.2f; stack %.2f; web 1.57' % (chan_depth, stack), 10),
              text(ox2, oy2 + SINK['depth'] + G + 14, 'guarded envelope %.1f x %.1f x %.1f'
                   % tuple(env_guard), 10)]

    # View 3: top opening plan
    ox3, oy3 = 15, 112
    parts += [text(ox3, oy3 - 4, 'VIEW 3 top opening 307 x 53 (received, cover on) with 215 x 48 control study', 12),
              rect(ox3, oy3, frame_w / 1.6, frame_d / 1.6, 'fill="#fafafa" stroke="#000"'),
              rect(ox3 + end_w / 1.6, oy3 + 2.5 / 1.6, controls_w / 1.6, controls_d / 1.6, 'fill="#cde" stroke="#345"'),
              rect(ox3, oy3 + (frame_d - env_guard[1]) / 3.2, env_guard[0] / 1.6, env_guard[1] / 1.6, GRD),
              rect(ox3 + x0 / 1.6, oy3 + y0 / 1.6, env_bare[0] / 1.6, env_bare[1] / 1.6, OUTL),
              text(ox3, oy3 + frame_d / 1.6 + 5, 'end zone %.1f wide; guarded sink needs %.1f (FAIL); bare %.1f '
                   '(corner overlap %.2f at published R%g). Scale 1:1.6 of other views.'
                   % (end_w, env_guard[0], env_bare[0], corner, R), 10)]

    # View 4: depth budget bars
    ox4, oy4 = 15, 160
    parts.append(text(ox4, oy4 - 4, 'VIEW 4 rear/side spare against search envelopes (bars to scale)', 12))
    rows = [('rear spare, 130 tray: %.0f' % (depth_avail - 130), depth_avail - 130),
            ('rear spare, 145 cage: %.0f' % (depth_avail - 145), depth_avail - 145),
            ('side spare total, 440 wide: %.0f' % (width_avail - 440), width_avail - 440),
            ('sink flat on wall, bare: %.2f' % flat_bare, flat_bare),
            ('sink flat on wall, guarded: %.2f' % flat_guard, flat_guard)]
    for i, (lab, val) in enumerate(rows):
        parts += [rect(ox4, oy4 + i * 5, val, 3.5, 'fill="%s" stroke="#000"' % ('#9c9' if i < 3 else '#f99')),
                  text(ox4 + 45, oy4 + i * 5 + 3, lab, 10)]
    fischer = result['flat_base_candidate']
    fw, fh, fd = fischer['guarded_width_height_depth_mm']
    parts += [text(183,16,'Fischer SK 81 50 SA, rear elevation',12),
              rect(183,24,fw*.8,fh*.8,GRD), rect(189,30,80,40,OUTL),
              text(183,24+fh*.8+5,'Required wall face %.2f x %.2f mm' % (fw,fh)),
              text(183,24+fh*.8+10,'Projection %.2f mm with guard and attachment' % fd),
              text(183,24+fh*.8+15,'Depth margins %+.2f / %+.2f mm (130 / 145 tray)' % (fischer['margin_130_tray_mm'],fischer['margin_145_cage_mm'])),
              text(183,24+fh*.8+20,'Vertical fins. Confirm cover and withdrawal clearance.')]
    parts.append('</svg>')
    OUT_SVG.write_text('\n'.join(parts) + '\n')
