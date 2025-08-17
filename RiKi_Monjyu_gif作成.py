import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image, ImageDraw, ImageFont
import imageio
from scipy.ndimage import gaussian_filter
import matplotlib.animation as animation
import time
import os

# 背景のサイズ設定
width, height = 500, 500
tile_size = 20
# 前半フレームのみ生成し、後半は逆再生
forward_frames = 60  # 前半部分（この後逆順で繰り返す）
total_frames = forward_frames * 2  # 前半 + 逆順再生で合計フレーム数

# 青系の色のグラデーションを作成（明るめから暗めへ）
dark_blue_colors = [(0.3, 0.6, 0.9), (0, 0.3, 0.7), (0, 0.15, 0.5), (0, 0.05, 0.3)]
blue_cmap = LinearSegmentedColormap.from_list('blue_cmap', dark_blue_colors)

# 光るセル用の位置をランダムに選ぶ - より多くのセルを設定
glowing_cells = []
for _ in range(45):  # 光るセルの数を増加
    i = np.random.randint(0, height // tile_size)
    j = np.random.randint(0, width // tile_size)
    duration = np.random.randint(8, 20)  # 光る持続時間を短くして変化を速く
    start_frame = np.random.randint(0, forward_frames)
    glowing_cells.append([i, j, duration, start_frame])

# 前半フレーム用の画像リスト
forward_images = []

# リアルタイム表示用の設定
fig, ax = plt.figure(figsize=(10, 10)), plt.gca()
plt.axis('off')
display = ax.imshow(np.zeros((height, width, 3)))
plt.tight_layout()

# 画像ファイルを読み込み、透過処理する関数
def prepare_overlay_image(image_path, transparency=0.5, blue_threshold=150):
    """
    画像ファイルを読み込み、青い部分を透過処理する
    
    image_path: 画像ファイルのパス
    transparency: 透明度（0-1の範囲、1は完全不透明）
    blue_threshold: 青と判定する閾値（0-255）
    """
    try:
        # 画像を読み込む
        img = Image.open(image_path).convert("RGBA")
        
        # リサイズ（必要に応じて）
        img = img.resize((width, height), Image.LANCZOS)
        
        # ピクセルデータを取得
        img_data = np.array(img)
        
        # 青い部分を判定し、アルファチャンネルを調整
        r, g, b, a = img_data[:, :, 0], img_data[:, :, 1], img_data[:, :, 2], img_data[:, :, 3]
        
        # より厳密な青の判定条件（青が高く、他の色が低い場合）
        # 青色の相対的な優位性も考慮
        blue_dominance = b - np.maximum(r, g)  # 青と他の色の最大値との差
        
        # 複数の条件で青を検出:
        # 1. 青の値が閾値より高い
        # 2. 青が他の色より一定以上強い
        # 3. 青が支配的な色（比率的に）
        is_blue = (b > blue_threshold) & (blue_dominance > 30) & (b > (r + g) * 0.5)
        
        # 青の強さに応じて透明度を調整（より青いほど透明に）
        blue_strength = blue_dominance / 255.0  # 正規化
        blue_strength = np.clip(blue_strength, 0, 1)  # 0-1の範囲に制限
        
        # アルファ値を調整（青の強さに応じた透明度を適用）
        a_new = a.copy()
        
        # 青い部分には透明度を適用
        blue_alpha = 255 - (blue_strength * 255 * (1 - transparency))
        a_new[is_blue] = blue_alpha[is_blue].astype(np.uint8)
        
        # 更新した配列から画像を作成
        processed_img = Image.fromarray(np.dstack((r, g, b, a_new)), "RGBA")
        
        # デバッグ用：青色が検出された領域を可視化
        debug_mask = np.zeros_like(img_data)
        debug_mask[is_blue, 2] = 255  # 青色検出部分を青く表示
        debug_mask[:, :, 3] = 255  # アルファを不透明に
        debug_img = Image.fromarray(debug_mask, "RGBA")
        debug_img.save("temp_detection_mask.png")
        
        return processed_img
    
    except Exception as e:
        print(f"画像読み込みエラー: {e}")
        # エラーの場合は単純な青い透過レイヤーを作成
        overlay = np.zeros((height, width, 4), dtype=np.uint8)
        overlay[:, :, 2] = 200  # 青チャンネル
        overlay[:, :, 3] = int(255 * transparency)  # アルファ
        return Image.fromarray(overlay, 'RGBA')

# 画像ファイルを読み込む（パスは適切に変更してください）
# 例：透過したい青い画像のパス
overlay_image_path = "_webUI/Monjyu/static/blue_Monjyu.png"  # この部分は実際の画像パスに変更

# 画像が存在するか確認
if os.path.exists(overlay_image_path):
    # 透明度を高く設定して青い部分をより透明に
    overlay_img = prepare_overlay_image(overlay_image_path, transparency=0.2, blue_threshold=130)
    print(f"画像 '{overlay_image_path}' を読み込み、青色部分を透過処理しました")
else:
    # 画像がない場合は単純な青いレイヤーを作成
    print(f"画像 '{overlay_image_path}' が見つかりません。代わりに単色の青いレイヤーを使用します。")
    overlay = np.zeros((height, width, 4), dtype=np.uint8)
    overlay[:, :, 2] = 200  # 青チャンネル
    overlay[:, :, 3] = int(255 * 0.3)  # 30%の透明度
    overlay_img = Image.fromarray(overlay, 'RGBA')

# フレームごとに画像を生成するアニメーション関数
def update(frame):
    # 前半部分のみ実際に生成し、後半はキャッシュから逆順に取得
    if frame < forward_frames:
        actual_frame = frame
    else:
        # 実際の生成処理はスキップして、すでに生成済みの画像を表示
        idx = total_frames - frame - 1  # 逆順インデックス
        img = forward_images[idx]
        
        # 表示を更新
        if frame % 10 == 0:
            print(f"Using cached frame for {frame+1}/{total_frames}")
        display.set_array(np.array(img))
        return [display]
    
    # 基本のタイルグリッドを作成
    grid = np.zeros((height // tile_size, width // tile_size))
    
    # 穏やかな波のパターンを生成
    x = np.linspace(0, 4*np.pi, grid.shape[1])
    y = np.linspace(0, 4*np.pi, grid.shape[0])
    X, Y = np.meshgrid(x, y)
    
    # ゆっくりとした複数の波を合成 - より激しい動きに調整
    wave = 0.3 * np.sin(X + actual_frame/8) + 0.3 * np.cos(Y + actual_frame/10)
    wave += 0.25 * np.sin(2*X - actual_frame/12) + 0.25 * np.cos(2*Y - actual_frame/15)
    wave += 0.2 * np.sin(X + Y + actual_frame/20)
    # さらに高周波の波を追加して変化を激しく
    wave += 0.1 * np.sin(3*X + actual_frame/5) + 0.1 * np.cos(3*Y - actual_frame/6)
    
    # 脈動効果：フレームの進行に応じて全体的な明るさを変化させる - より強い変化に
    brightness_phase = actual_frame / forward_frames
    # 明るさを変化（0.75～1.0）し、サイン波の周期を1回に
    brightness_factor = 0.75 + 0.25 * np.sin(brightness_phase * np.pi - np.pi/2)
    
    # セルが光る効果を追加
    glow_grid = np.zeros_like(grid)
    for i, (cell_i, cell_j, duration, start_frame) in enumerate(glowing_cells):
        if actual_frame >= start_frame and actual_frame < start_frame + duration:
            # 時間に応じて輝度を変化させる（最大値は中間フレーム）
            phase = (actual_frame - start_frame) / duration
            intensity = np.sin(phase * np.pi)  # 0～1～0のサイン波
            
            # 光るセルとその周辺に輝きを追加 - 強度を上げる
            radius = 3  # 影響範囲を拡大
            for di in range(-radius, radius+1):
                for dj in range(-radius, radius+1):
                    ni, nj = cell_i + di, cell_j + dj
                    if 0 <= ni < grid.shape[0] and 0 <= nj < grid.shape[1]:
                        # 中心からの距離に応じて輝度を減衰
                        dist = np.sqrt(di**2 + dj**2)
                        if dist <= radius:
                            glow = intensity * (1 - dist/radius) * 0.9  # 最大で0.9の追加輝度に増加
                            glow_grid[ni, nj] += glow
            
        # 持続時間が終わったらリセット - よりランダムな配置に
        if actual_frame >= start_frame + duration:
            glowing_cells[i] = [
                np.random.randint(0, height // tile_size),
                np.random.randint(0, width // tile_size),
                np.random.randint(5, 15),  # より短い持続時間
                actual_frame + np.random.randint(0, 10)  # より早く次のセルが光り始める
            ]
    
    # 通常の波に光るセルの効果を加える
    grid = wave + glow_grid
    
    # スムーズにするためのぼかし
    grid = gaussian_filter(grid, sigma=0.6)
    
    # タイルグリッドから画像を作成
    img_array = np.zeros((height, width, 3))
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            # 色の値を0-1の範囲に正規化
            val = (grid[i, j] + 1) / 2
            val = np.clip(val, 0, 1)  # 0-1の範囲に収める
            
            # 明るさ因子を適用
            color = blue_cmap(val)[:3]  # RGBのみ取得
            # 全体の明るさを調整（暗いスタートから明るくなる）
            adjusted_color = [c * brightness_factor for c in color]
            
            # タイルを描画
            img_array[i*tile_size:(i+1)*tile_size, j*tile_size:(j+1)*tile_size] = adjusted_color
    
    # PILイメージに変換
    base_img = Image.fromarray((img_array * 255).astype(np.uint8))
    
    # RGBA形式に変換
    rgba_base = base_img.convert("RGBA")
    
    # 透過処理した画像を重ねる
    composite_img = Image.alpha_composite(rgba_base, overlay_img)
    
    # 表示・保存用にRGBに変換
    final_img = composite_img.convert("RGB")
    
    # 前半部分の画像をキャッシュ
    forward_images.append(final_img)
    
    # 表示を更新（10フレームごとに進捗表示）
    if frame % 10 == 0:
        print(f"Generating frame {frame+1}/{total_frames} (Brightness: {brightness_factor:.2f})")
    display.set_array(np.array(final_img))
    
    return [display]

# アニメーションを実行
print("Starting real-time animation preview...")
ani = animation.FuncAnimation(fig, update, frames=total_frames, interval=100, repeat=False, blit=True)
plt.show()

# 全フレーム生成後、GIFを保存
print("Creating pulsating seamless loop GIF with image overlay...")

# 前半で生成した画像と後半の逆順画像を結合
all_images = forward_images + forward_images[-2:0:-1]  # 最初と最後のフレームが重複しないように

# GIFを作成
imageio.mimsave('_webUI/Monjyu/static/icon_Monjyu.gif', all_images, duration=0.2)  # 0.2秒/フレーム = 5 FPS でより速く
print("GIF animation has been created as '_webUI/Monjyu/static/icon_Monjyu.gif'")

# 最終結果を表示
plt.figure(figsize=(8, 8))
plt.imshow(np.array(forward_images[0]))
plt.axis('off')
plt.title("First Frame with Image Overlay")
plt.show()

plt.figure(figsize=(8, 8))
plt.imshow(np.array(forward_images[-1]))
plt.axis('off')
plt.title("Last Frame with Image Overlay")
plt.show()