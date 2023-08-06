import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

class SSPQDD(object):

    def __init__(self):
        self.model = tf.lite.Interpreter(model_path='./converted_model.tflite')
        self.model.allocate_tensors()

        self.input_details = self.model.get_input_details()
        self.output_details = self.model.get_output_details()

    def pre_process(self,sig,maxim,minim):

        if len(sig) > 3000:
            a = 0
            b = 9
            new = []
            for i in range(3000):
                window = sig[a:b]
                new.append(np.max(window))
                a += 10
                b += 10
        else:
            new = sig
        sig_norm = [(2/(maxim-minim))*new[i] for i in range(len(new))]
        signal = np.array(sig_norm)

        signal.shape=(tuple(self.input_details[0]['shape']))

        return signal

    def infer(self,sig,num_grid=188):
        self.model.set_tensor(self.input_details[0]['index'], np.asarray(sig).astype('float32'))
        self.model.invoke()

        class_out = self.model.get_tensor(self.output_details[0]['index'])
        conf_out = self.model.get_tensor(self.output_details[1]['index'])

        pred_conf = np.array(tf.transpose(conf_out))
        pred_conf.shape = (2, num_grid)
        pred_class = np.array(tf.transpose(class_out))
        pred_class.shape = (6, num_grid)

        return pred_class,  pred_conf

    def post_process(self,class_out,conf_out):
        ind = [i for i, x in enumerate(conf_out[0]) if x > 0.9]
        boxes = []
        try:
            start = ind[0]
            # print(len(ind))
            if len(ind) == 1:
                block = {'start': (start * 16)-16,
                         'stop': (start * 16)+16}
                boxes.append(block)
            else:
                for i in range(len(ind) - 1):
                    if ind[i + 1] - ind[i] == 1:
                        block = {'start': start * 16,
                                 'stop': ind[i + 1] * 16}
                    elif ind[i + 1] - ind[i] != 1:
                        boxes.append(block)
                        start = ind[i + 1] * 16
                boxes.append(block)

            classi = class_out[:, ind[0]]
            ind_class = np.argmax(classi)

            return boxes, ind_class
        except:

            ind_class = []
            return boxes, ind_class

if __name__ == '__main__':
    time = np.arange(0, 3.75, 1 / 8000)

    amplitude = 10*np.sin(2 * 50 * np.pi * time)
    amplitude[1600:1600 + 1600] = 1.5 * amplitude[1600:1600 + 1600]
    # ind = 1600
    # impulse = 9
    # amplitude[ind] = impulse
    sig = SSPQDD().pre_process(amplitude, 10, -10)
    class_out, conf_out = SSPQDD().infer(sig)
    boxes, ind_class = SSPQDD().post_process(class_out, conf_out)
    #print(np.reshape(sig,(3000,)))
    fig, axs = plt.subplots(2)
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'black']
    axs[0].plot(10*np.reshape(sig,(3000,)))
    axs[0].set_xlim([0, 3000])
    axs[0].set_ylim([-15, 15])

    for box in range(3):
        rect = plt.Rectangle((boxes[0]['start'], 12.5), boxes[0]['stop'] - boxes[0]['start'], -25, linewidth=1,
                             edgecolor=colors[ind_class], facecolor='none', zorder=2)
        axs[0].add_patch(rect)
    axs[1].plot(amplitude)
    axs[1].set_xlim([0, len(amplitude)])
    axs[1].set_ylim([-15, 15])
    for box in range(3):
        rect = plt.Rectangle((boxes[0]['start']*10, 12.5), boxes[0]['stop']*10 - boxes[0]['start']*10, -25, linewidth=1,
                             edgecolor=colors[ind_class], facecolor='none', zorder=2)
        axs[1].add_patch(rect)
    plt.show()

    print(boxes)