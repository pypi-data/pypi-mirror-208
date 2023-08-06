import model_esthetics_visualizer as viz
import pyaf.Bench.TS_datasets as tsds

lDataset = tsds.load_ozone()

lVisualizer = viz.cModelEstheticsVisualizer()

lVisualizer.generate_video(lDataset)
