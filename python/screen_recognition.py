import sys
print(sys.path)
import cv2
import numpy as np
import pyautogui
import time
import chess
import chess.engine
import os
from PIL import Image
import pytesseract
import threading

# Set path to tesseract executable - update this path as needed
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class ChessRecognition:
    def __init__(self):
        self.board = chess.Board()
        self.engine = None  # Remove engine initialization
        self.is_playing = False
        self.player_color = chess.WHITE  # Default player is white
        self.ai_thinking = False
        
        # Remove engine initialization code
        print("Chess engine initialization skipped. Using python-chess for AI moves.")
    
    def __del__(self):
        # Clean up engine when object is destroyed
        if self.engine:
            self.engine.quit()
    
    def capture_screen(self):
        """Capture the current screen"""
        screenshot = pyautogui.screenshot()
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    def find_chessboard(self, image):
        """Detect a chessboard in the given image"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY, 11, 2)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by size and shape
        possible_boards = []
        for contour in contours:
            # Approximate the contour
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            
            # If it has 4 corners (square/rectangle)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check if it's roughly square (aspect ratio close to 1)
                aspect_ratio = float(w) / h
                if 0.8 <= aspect_ratio <= 1.2 and w > 200 and h > 200:  # Minimum size check
                    possible_boards.append((x, y, w, h))
        
        # Return the largest possible chessboard
        if possible_boards:
            return max(possible_boards, key=lambda b: b[2] * b[3])  # Return the largest by area
        return None
    
    def detect_chess_pieces(self, image, board_rect):
        """Detect chess pieces on the board"""
        x, y, w, h = board_rect
        board_img = image[y:y+h, x:x+w]
        
        # Resize to standard size
        board_img = cv2.resize(board_img, (800, 800))
        
        # Calculate square size
        square_size = 800 // 8
        
        # Initialize empty board representation
        piece_positions = [[None for _ in range(8)] for _ in range(8)]
        
        # Process each square
        for row in range(8):
            for col in range(8):
                # Extract square
                square_x = col * square_size
                square_y = row * square_size
                square_img = board_img[square_y:square_y+square_size, square_x:square_x+square_size]
                
                # Detect if piece is present (simplified)
                gray_square = cv2.cvtColor(square_img, cv2.COLOR_BGR2GRAY)
                _, binary = cv2.threshold(gray_square, 100, 255, cv2.THRESH_BINARY)
                white_pixels = cv2.countNonZero(binary)
                black_pixels = square_size * square_size - white_pixels
                
                # Determine if square has a piece and what color
                # This is a simplified approach - would need refinement for real use
                if white_pixels > 0.7 * (square_size * square_size):
                    # Likely empty square
                    piece_positions[row][col] = None
                elif white_pixels > black_pixels:
                    # Likely white piece
                    piece_positions[row][col] = 'w'
                else:
                    # Likely black piece
                    piece_positions[row][col] = 'b'
        
        return piece_positions
    
    def recognize_board_state(self):
        """Capture screen and recognize the chess board state"""
        # Capture screen
        screen = self.capture_screen()
        
        # Find chessboard
        board_rect = self.find_chessboard(screen)
        if not board_rect:
            return None, "No chessboard detected on screen"
        
        # Detect pieces
        piece_positions = self.detect_chess_pieces(screen, board_rect)
        
        # Convert to FEN (Forsyth-Edwards Notation)
        # This is a simplified version and would need refinement
        fen = self.positions_to_fen(piece_positions)
        
        return board_rect, fen
    
    def positions_to_fen(self, positions):
        """Convert piece positions to FEN string (simplified)"""
        # This is a placeholder - actual implementation would be more complex
        # and would need to identify specific pieces (pawn, knight, etc.)
        fen_rows = []
        
        for row in positions:
            empty_count = 0
            fen_row = ""
            
            for square in row:
                if square is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen_row += str(empty_count)
                        empty_count = 0
                    
                    # Placeholder - would need to identify actual piece types
                    if square == 'w':
                        fen_row += 'P'  # Assume white pawn for simplicity
                    else:
                        fen_row += 'p'  # Assume black pawn for simplicity
            
            if empty_count > 0:
                fen_row += str(empty_count)
            
            fen_rows.append(fen_row)
        
        # Join rows with slashes
        fen = "/".join(fen_rows)
        
        # Add other FEN components (active color, castling, etc.)
        # For simplicity, using placeholder values
        fen += " w KQkq - 0 1"
        
        return fen
    
    def start_chess_game(self, player_color="white"):
        """Start a new chess game"""
        self.board = chess.Board()
        self.is_playing = True
        
        if player_color.lower() == "white":
            self.player_color = chess.WHITE
            print("You are playing as White. Your move first.")
            return "You are playing as White. Your move first."
        else:
            self.player_color = chess.BLACK
            print("You are playing as Black. I'll move first.")
            ai_move = self.get_ai_move()
            self.board.push(ai_move)
            return f"You are playing as Black. I'll move first. I play {ai_move.uci()}"
    
    def get_ai_move(self):
        """Get a move from the chess engine"""
        # Use python-chess to make a random legal move
        legal_moves = list(self.board.legal_moves)
        if legal_moves:
            return legal_moves[np.random.randint(0, len(legal_moves))]
        return None
    
    def make_move(self, move_str):
        """Make a move on the board"""
        try:
            # Parse the move string
            move = chess.Move.from_uci(move_str)
            
            # Check if move is legal
            if move in self.board.legal_moves:
                # Make the move
                self.board.push(move)
                
                # Check game state
                if self.board.is_checkmate():
                    return "Checkmate! You win!", True
                elif self.board.is_stalemate():
                    return "Stalemate! The game is a draw.", True
                
                # AI's turn
                ai_move = self.get_ai_move()
                if ai_move:
                    self.board.push(ai_move)
                    
                    # Check game state after AI move
                    if self.board.is_checkmate():
                        return f"I play {ai_move.uci()}. Checkmate! I win!", True
                    elif self.board.is_stalemate():
                        return f"I play {ai_move.uci()}. Stalemate! The game is a draw.", True
                    
                    return f"I play {ai_move.uci()}", False
                else:
                    return "I couldn't find a valid move.", True
            else:
                return f"Invalid move: {move_str}. Please try again.", False
        except ValueError:
            return f"Invalid move format: {move_str}. Please use UCI format (e.g., e2e4).", False
    
    def get_board_state(self):
        """Get the current board state as a string"""
        return str(self.board)
    
    def is_game_over(self):
        """Check if the game is over"""
        return self.board.is_game_over()
    
    def get_game_result(self):
        """Get the result of the game"""
        if not self.board.is_game_over():
            return "Game still in progress"
        
        if self.board.is_checkmate():
            # Determine who won
            if self.board.turn == self.player_color:
                return "Checkmate! I win!"
            else:
                return "Checkmate! You win!"
        elif self.board.is_stalemate():
            return "Stalemate! The game is a draw."
        elif self.board.is_insufficient_material():
            return "Draw due to insufficient material."
        elif self.board.is_fifty_moves():
            return "Draw due to fifty-move rule."
        elif self.board.is_repetition():
            return "Draw due to threefold repetition."
        else:
            return "Game over."

def detect_screen_content():
    """Detect what's on screen and return a description"""
    # Initialize chess recognition
    chess_rec = ChessRecognition()
    
    # Capture screen
    screen = chess_rec.capture_screen()
    
    # Check for chessboard
    board_rect = chess_rec.find_chessboard(screen)
    if board_rect:
        return "I can see a chess board on your screen. Would you like to play a game of chess?"
    
    # If no chessboard, try OCR to get general content
    try:
        # Convert to PIL Image for tesseract
        pil_image = Image.fromarray(cv2.cvtColor(screen, cv2.COLOR_BGR2RGB))
        
        # Extract text
        text = pytesseract.image_to_string(pil_image)
        
        # Analyze text content (simplified)
        if text:
            if "chess" in text.lower():
                return "I see something related to chess on your screen. Would you like to play?"
            
            # Return a summary of detected text
            words = text.split()
            if len(words) > 20:
                return f"I can see text on your screen. It starts with: {' '.join(words[:20])}..."
            else:
                return f"I can see text on your screen: {text}"
        else:
            return "I can see your screen, but I don't recognize any specific content."
    except Exception as e:
        return f"I can see your screen, but I had trouble analyzing it: {str(e)}"

# Function to be called from conversation.py
def handle_screen_recognition(user_input, tts, stt=None):
    """Handle screen recognition commands"""
    # Initialize chess recognition
    chess_rec = ChessRecognition()
    
    # Check if user wants to play chess
    if "play chess" in user_input.lower():
        # Ask for color preference
        tts.speak("Would you like to play as white or black?")
        if stt:
            color_choice = stt.start_listening(tts=tts)
            if color_choice:
                if "black" in color_choice.lower():
                    response = chess_rec.start_chess_game("black")
                else:
                    # Default to white
                    response = chess_rec.start_chess_game("white")
                tts.speak(response)
                
                # Start game loop
                game_over = False
                while not game_over and chess_rec.is_playing:
                    if not chess_rec.is_game_over():
                        tts.speak("Your move. Please say your move in UCI format, like e2e4.")
                        move_input = stt.start_listening(tts=tts)
                        
                        if move_input:
                            if "quit" in move_input.lower() or "exit" in move_input.lower() or "stop" in move_input.lower():
                                tts.speak("Ending the chess game.")
                                chess_rec.is_playing = False
                                break
                            
                            # Clean up the move input
                            move_str = ''.join(c for c in move_input.lower() if c.isalnum())
                            
                            # Make the move
                            response, game_over = chess_rec.make_move(move_str)
                            tts.speak(response)
                            
                            # Show current board state
                            print(chess_rec.get_board_state())
                    else:
                        # Game is over
                        result = chess_rec.get_game_result()
                        tts.speak(result)
                        game_over = True
            else:
                tts.speak("I didn't hear your color choice. Let's try again later.")
        else:
            tts.speak("I need speech recognition to play chess. Let's try again later.")
        return
    
    # Check if user wants to know what's on screen
    if "what's on my screen" in user_input.lower() or "what do you see" in user_input.lower():
        # Start screen recognition in a separate thread to avoid blocking
        def recognize_and_respond():
            description = detect_screen_content()
            tts.speak(description)
        
        threading.Thread(target=recognize_and_respond).start()
        return
    
    # Default response
    tts.speak("I can recognize chess boards on your screen. Try saying 'what's on my screen' or 'play chess'.")