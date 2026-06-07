import time

class VirtualAVSystem:
    def __init__(self):
        # 1. PHYSICAL WIRING STATES (True = Connected, False = Disconnected)
        # Trainees can toggle these to simulate broken/unplugged hardware
        self.cables = {
            "IN1606_Power": True,       # Power from conditioner [cite: 3]
            "MLC_PoE": True,            # Connected to PoE port (VLAN 116) [cite: 27]
            "Laptop_VGA": True,         # Input 1 [cite: 4]
            "PC_HDMI": True,            # Input 3 [cite: 6]
            "DocCam_HDMI": True,        # Input 4 [cite: 7]
            "Aux_HDMI": True,           # Input 6 [cite: 9]
            "IN1606_To_Monitor": True,  # Output A to NEC monitor [cite: 10]
            "IN1606_To_Tx": True,       # Output B to DTP Tx [cite: 11, 31]
            "Tx_To_Rx_DTP": True,       # DTP Cable Cat50 link 
            "Rx_To_Projector": True,    # HDMI Output to Epson 
            "MLC_To_Tx_RS232": True,    # COM 1 Control [cite: 21, 33]
            "Rx_To_Proj_RS232": True,   # Rx to Epson RS-232C control [cite: 40, 45]
            "MLC_To_DocCam_RS232": True # COM 2 Control to Elmo [cite: 22, 49]
        }

        # 2. DEVICE OPERATIONAL STATES
        self.system_power = "OFF"       # "OFF", "WARMING", "ON" [cite: 55, 70, 99]
        self.selected_source = "PC"     # Defaults to PC on boot 
        self.is_muted = False           # Video mute state 
        self.volume_level = 50          # 0 to 100 range [cite: 78]
        self.screen_state = "UP"        # Screen relay position [cite: 26, 57, 100]
        
        # Hardware power baselines
        self.pc_power_on = True         # Left on at all times per instructions 
        self.doc_cam_power_on = False   # Manually operated [cite: 90, 101]

    def press_power_on(self):
        """Simulates pressing the 'ON' button on the MLC Plus 200 panel."""
        if not self.cables["MLC_PoE"]:
            print("[ERROR] Control panel has no power! Check PoE network connection.") [cite: 20, 27]
            return
        
        if self.system_power == "ON":
            print("[Info] System is already fully operational.")
            return

        print("\n=== STARTING SYSTEM SYSTEM UP ===") [cite: 55]
        self.system_power = "WARMING"
        print("Activating Screen Down Relays (Relay 2 -> COMMON)...") [cite: 26]
        self.screen_state = "DOWN" [cite: 57]
        
        print("Simulating 30-second system warm-up...") [cite: 70]
        # Text-based simulated delay
        time.sleep(1) 
        
        self.system_power = "ON"
        self.selected_source = "PC" # Auto-defaults 
        print(f"System is ON. Screen is {self.screen_state}. Default source set to PC.") [cite: 57, 71]
        self.evaluate_signal_paths()

    def press_power_off(self):
        """Simulates holding down the 'OFF' button.""" [cite: 99]
        print("\n=== SHUTTING DOWN SYSTEM ===") [cite: 98]
        self.system_power = "OFF"
        print("Activating Screen Up Relays (Relay 1 -> COMMON)...") [cite: 26]
        self.screen_state = "UP" [cite: 100]
        print("System is now OFF. Screen is raised.") [cite: 100]

    def select_source(self, source_name):
        """Simulates pushing a source button: 'PC', 'VGA', 'HDMI', or 'DOC_CAM'.""" [cite: 75]
        if self.system_power != "ON":
            print("[Warning] System is not powered ON. Cannot switch sources.")
            return
        
        valid_sources = ["PC", "VGA", "HDMI", "DOC_CAM"]
        if source_name not in valid_sources:
            print(f"[Error] Invalid source '{source_name}' selected.")
            return

        self.selected_source = source_name
        print(f"\n[Button Press] Source switched to: {source_name}") [cite: 76]
        self.evaluate_signal_paths()

    def toggle_mute(self):
        """Toggles the video mute function.""" [cite: 94]
        if self.system_power == "ON":
            self.is_muted = not self.is_muted
            print(f"\n[Button Press] Video Mute is now: {'ENABLED (Red Light)' if self.is_muted else 'DISABLED'}") [cite: 96]
            self.evaluate_signal_paths()

    def evaluate_signal_paths(self):
        """
        The Core Logic Matrix. Evaluates variables to determine exactly
        what is being outputted on the Local Monitor and the Projector Screen.
        """
        print("--- Signal Path Evaluation ---")
        
        # Check basic switcher infrastructure power [cite: 3]
        if not self.cables["IN1606_Power"]:
            print("[SIGNAL dead] Extron IN1606 Matrix Switcher has no power.")
            return

        # Map button selection to the structural physical IN1606 inputs [cite: 4, 6, 7, 9]
        source_to_input_map = {
            "VGA": ("INPUT 1 (Laptop VGA)", self.cables["Laptop_VGA"], True),
            "PC": ("INPUT 3 (Installed PC)", self.cables["PC_HDMI"], self.pc_power_on),
            "DOC_CAM": ("INPUT 4 (Doc Camera)", self.cables["DocCam_HDMI"], self.doc_cam_power_on),
            "HDMI": ("INPUT 6 (Aux HDMI)", self.cables["Aux_HDMI"], True)
        }

        input_name, video_cable_connected, source_device_ready = source_to_input_map[self.selected_source]

        # 1. Evaluate Local Monitor Path (Output A) [cite: 10]
        if video_cable_connected and source_device_ready:
            if self.cables["IN1606_To_Monitor"]:
                local_monitor_output = f"Displaying {input_name}"
            else:
                local_monitor_output = "No Signal (Cable broken/unplugged between Switcher and Local Monitor)"
        else:
            local_monitor_output = f"No Signal (Source device inactive or input cable unplugged)"

        # 2. Evaluate Projector Path (Output B through DTP Extension) [cite: 11, 31]
        projector_output = "No Signal"
        
        if self.is_muted:
            projector_output = "Muted / Blanked (Video blanking active)" [cite: 94]
        elif not (video_cable_connected and source_device_ready):
            projector_output = f"No Signal (No valid stream feeding input)"
        else:
            # Trace the structural physical DTP connection path [cite: 31, 32, 38]
            if not self.cables["IN1606_To_Tx"]:
                projector_output = "No Signal (Disconnected between Switcher Output B and DTP Tx Input)" [cite: 11, 31]
            elif not self.cables["Tx_To_Rx_DTP"]:
                projector_output = "No Signal (DTP link broken between Tx and Rx units)" [cite: 32, 39]
            elif not self.cables["Rx_To_Projector"]:
                projector_output = "No Signal (HDMI cable disconnected between DTP Rx and Projector Input 1)" [cite: 38, 44]
            else:
                # Check control path infrastructure for projector power/wake automation [cite: 33, 40]
                control_ok = self.cables["MLC_To_Tx_RS232"] and self.cables["Rx_To_Proj_RS232"] [cite: 33, 40]
                if control_ok:
                    projector_output = f"Projecting {input_name} perfectly at 16:10 aspect ratio"
                else:
                    projector_output = "No Control (Cables connected, but Projector missed RS-232 wake sequence)" [cite: 33, 40]

        # Output Results to the Virtual Terminal Console
        print(f"[*] LOCAL MONITOR : {local_monitor_output}") [cite: 56, 94]
        print(f"[*] WALL PROJECTOR: {projector_output}") [cite: 94]
        print("------------------------------")

# --- SIMULATING AN ACTIVE TRAINING RUN ---
if __name__ == "__main__":
    # Instantiate the virtual room configuration
    room101 = VirtualAVSystem()
    
    # 1. Faculty arrives and powers on the system
    room101.press_power_on()
    
    # 2. Faculty switches to the Document Camera, but forgot to turn it on!
    room101.select_source("DOC_CAM")
    
    # 3. Faculty turns on the physical Document Camera device [cite: 90]
    print("\n[Action] Faculty reaches over and powers on the ELMO Document Camera manually...")
    room101.doc_cam_power_on = True
    room101.evaluate_signal_paths()
    
    # 4. TECH SUPPORT TROUBLESHOOTING SIMULATION
    # A cable is unplugged behind the rack (e.g., the DTP link between transmitter and receiver) 
    print("\n!!! TROUBLESHOOTING SCENARIO: A student trips over a cable behind the rack !!!")
    room101.cables["Tx_To_Rx_DTP"] = False # Unplugging the cable 
    
    # Faculty tries to go back to the PC input
    room101.select_source("PC")
    
    # 5. Faculty leaves and shuts system down [cite: 98]
    room101.press_power_off()