from flask import Flask, render_template, Response
import cv2
import pyzbar.pyzbar as pyzbar
from pylibdmtx.pylibdmtx import decode


app = Flask(__name__)

camera = cv2.VideoCapture(0)


def decode_display(image):
    """Decoding detected codes, using two different decoding libraries, pylibdmtx for data matrices,
     and pyzbar, for one-dimensional barcodes and QR codes"""

    data_matrices = decode(image, 1)  # pylibdmtx (used for decoding data matrix codes)
    barcodes = pyzbar.decode(image)  # pyzbar (used for decoding one-dimensional barcodes and QR codes)
    data = ""

    for barcode in barcodes:
        data = barcode.data.decode("utf-8")

    for data_matrix in data_matrices:
        data = data_matrix.data.decode("utf-8")

    return image, data


def print_results(data):
    if data:
        print("[INFO] Found code: {}".format(data))


def save_data_to_file(data):
    if data:
        with open("data.txt", 'w') as f:
            f.write(data)


def read_data_from_file(data_file):
    with open(data_file, 'r') as f:
        data = f.read()
    return data


def clear_data_file(data_file):
    with open(data_file, 'w') as f:
        f.close()


def detect(frame):
    """Enabling camera stream and printing results"""
    # frame = np.array(frame)
    im, data = decode_display(frame)
    save_data_to_file(data)
    # cv2.waitKey(1)
    # cv2.imshow("Scanner", im)
    print_results(data)
    # camera.release()
    # cv2.destroyAllWindows()
    return data


def gen_frames():  # generate frame by frame from camera
    while True:
        data = read_data_from_file("data.txt")
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            detect(frame)
            cv2.rectangle(frame, (0, frame.shape[0]), (frame.shape[1], int(0.92 * frame.shape[0])), (0, 0, 0), -1)
            buffer = cv2.putText(frame,
                                 data,
                                 (0, int(0.98 * frame.shape[0])),
                                 cv2.FONT_HERSHEY_SIMPLEX, 1,
                                 (255, 255, 255),
                                 2,
                                 cv2.LINE_AA)
            ret, buffer = cv2.imencode('.jpg', frame)
            new_frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + new_frame + b'\r\n')  # concat frame one by one and show result


@app.route('/video_feed')
def video_feed():
    # Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')



if __name__ == '__main__':
    clear_data_file("data.txt")
    app.run(debug=False)



