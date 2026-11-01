# PAI Final Project: Autonomous Patrol & Obstacle Avoidance Robot

Physical AI 応用講座の最終課題用リポジトリです。
ROS 2とIgnition Gazeboを使用し、AI（PyTorchによる画像テンソル処理）を用いた自律パトロールおよび障害物回避ロボットのシミュレーションを実装しています。

## 概要 (Overview)
ロボットが閉鎖空間（10m × 10mの赤い壁で囲まれたコース）を自律的にパトロールします。
車載カメラの画像をPyTorchテンソルに変換して異常スコア（壁への近接度）を算出し、壁の衝突直前で自動停止・回避行動を行うステートマシンを実装しています。

## 主要ファイル (Files)
* `world.sdf` : シミュレーション環境定義ファイル。ロボット本体、カメラセンサー、差動二輪プラグイン、および周囲を囲む赤い壁（障害物）を配置。
* `ai_patrol.py` : ROS 2の制御用Pythonノード。カメラ画像を受け取り、AI推論（テンソル演算）による距離判定と状態制御を行います。

## システム要件 (Requirements)
* Ubuntu 22.04
* ROS 2 Humble
* Ignition Gazebo (Fortress / Harmonic)
* Python libraries: `torch`, `opencv-python`, `cv_bridge`, `numpy`

## 制御ロジック (State Machine)
単に障害物を避けるだけでなく、処理落ちによる無限ループや壁への接触を防ぐため、以下の4つの状態（State）を持たせています。
1. **PATROL (パトロール)**: 通常速度で直進。カメラ画像の赤色ピクセル数が閾値（45,000,000）を超えたら `STOP` へ遷移。
2. **STOP (停止待機)**: 壁を検知後、一定フレーム完全に停止して挙動を安定させる。
3. **TURN (旋回)**: その場で左に約90度旋回する。
4. **ESCAPE (離脱)**: 旋回後、AI検知を一時的に無視して一定時間強制的に直進し、壁から確実に距離を取ってから `PATROL` へ戻る。

## 実行方法 (How to Run)
1. **Gazeboの起動**
   ターミナルを開き、SDFファイルのあるディレクトリで以下を実行します。
   ```bash
   ign gazebo world.sdf

ROS 2 - Gazebo ブリッジの起動 (必要な場合)
カメラ画像や速度指令を通信するため、別ターミナルでブリッジを起動します。

Bash
ros2 run ros_gz_bridge parameter_bridge /camera/image_raw@sensor_msgs/msg/Image@ignition.msgs.Image /model/my_robot/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist
AIパトロールノードの実行
さらに別ターミナルを開き、制御スクリプトを実行します。

Bash
python3 ai_patrol.py   
