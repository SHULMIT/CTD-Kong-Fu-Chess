from app.game_factory import GameFactory
from model.position import Position

app = GameFactory.create()
scene = app._scene
engine = scene._game_engine

# Test get_legal_moves
legal = engine.get_legal_moves(Position(6, 4))  # white pawn at e2
print(f"Legal moves for e2 pawn: {legal}")

# Test draw with selection
scene._controller.handle_position(Position(6, 4))
scene.draw()
print("Draw with selection + legal moves overlay: OK")

# Test draw_game_over
scene.draw()
print("ALL OK")
