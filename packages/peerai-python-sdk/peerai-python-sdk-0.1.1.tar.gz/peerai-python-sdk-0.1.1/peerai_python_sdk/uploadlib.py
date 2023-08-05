# from multiformats import CID, multihash
# data = b"Hello world!"
# digest = multihash.digest(data, "sha2-256")

from ipfs_cid import cid_sha256_hash
import onnx
from .get_upload_url import get_upload_url, get_model_upload_url
from .upload_google_cloud import upload_google_cloud
import os
from pathlib import Path
import onnx
import tempfile
import onnx_tool
import numpy as np
from onnx_tool.node import _get_shape, RESIZE_LINEAR_MACS, RESIZE_CUBIC_MACS
import requests
import json
from onnx_tool.tensor import is_valid_ndarray, volume
from onnxruntime.quantization import quantize_static, quantize_dynamic, QuantType

@onnx_tool.NODE_REGISTRY.register()
class ScatterNDNode(onnx_tool.Node):
    def shape_infer(self, intensors: [np.ndarray]):
        return [_get_shape(intensors[0])]
    # def value_infer(self, intensors: []):
    #     data = intensors[0]
    #     indices = intensors[1]
    #     updates = intensors[2]
    #     return [scatter_nd_impl(data, indices, updates)]
    
@onnx_tool.NODE_REGISTRY.register()
class ResizeNode(onnx_tool.Node):
    def shape_infer(self, intensors: [np.ndarray]):
        xshape = _get_shape(intensors[0])
        roi = []
        sizes = []
        if len(intensors) == 2:
            scales = intensors[1]
        elif len(intensors) >= 3:
            roi = intensors[1]
            scales = intensors[2]
            if len(intensors) >= 4:
                sizes = intensors[3]

        newshape = []
        if is_valid_ndarray(sizes):
            if len(sizes) == 4 or len(sizes) == 3:
                newshape = sizes
            if len(sizes) == 2:
                newshape = xshape[:2] + sizes
        else:
            if is_valid_ndarray(scales):
                newshape = []
                for src, scale in zip(xshape, scales):
                    newshape.append(math.floor(src * scale))

        if is_valid_ndarray(newshape):
            if newshape.dtype != np.int64:
                newshape = newshape.astype(dtype=np.int64)
        return [list(newshape)]

    def profile(self, intensors: [], outtensors: []):
        macs = 0
        outvol = volume(_get_shape(outtensors[0]))
        if self.mode == b'nearest':
            outvol *= 0
        elif self.mode == b'linear':
            outvol *= RESIZE_LINEAR_MACS
        elif self.mode == b'cubic':
            outvol *= RESIZE_CUBIC_MACS
        macs += outvol
        return macs
    
@onnx_tool.NODE_REGISTRY.register()
class TriluNode(onnx_tool.Node):
    # you can implement either shape_infer(faster) or value_infer.
    # it's not necessary to implement both
    def shape_infer(self, intensors):
        # if you know how to calculate shapes of this op, you can implement shape_infer
        return [_get_shape(intensors[0])]

@onnx_tool.NODE_REGISTRY.register()
class ModNode(onnx_tool.Node):
    # you can implement either shape_infer(faster) or value_infer.
    # it's not necessary to implement both
    def shape_infer(self, intensors):
        # if you know how to calculate shapes of this op, you can implement shape_infer
        return [_get_shape(intensors[0])]
    
    #for upgrade of node_profilers.py, node_profilers.py's 'infer_shape' method should be placed
    #as 'value_infer' method here, and do not create this class' 'shape_infer' method. 
    def value_infer(self, intensors: []):
        return [intensors[0]]

    def profile(self, intensors: [], outtensors: []):
        macs = 0
        # accumulate macs here
        # this node has no calculation
        return macs
    
data_type_map = {
    0: "undefined",
    1: "float32",
    2: "uint8",
    3: "int8",
    4: "uint16",
    5: "int16",
    6: "int32",
    7: "int64",
    8: "string",
    9: "bool",
    10: "float16",
    11: "double",
    12: "uint32",
    13: "uint64",
    14: "complex64",
    15: "complex128",
    16: "bfloat16"
}

from onnx_tool.graph import Graph
import onnx
import numpy as np


def get_macs(model, inputsSpec, outputsSpec, input_shapes=None, output_shapes=None):
    inputsData = {}
    for i,inpSpec in enumerate(inputsSpec):
        if input_shapes is not None and i < len(input_shapes):
            inpSpec['dims'] = input_shapes[i]
        if inpSpec['dataType'] == 'float32':
            inputsData[inpSpec['name']] = np.ones(inpSpec['dims'],np.float32)
        elif inpSpec['dataType'] == 'int32':
            inputsData[inpSpec['name']] = np.ones(inpSpec['dims'],np.int32)
        elif inpSpec['dataType'] == 'int64':
            inputsData[inpSpec['name']] = np.ones(inpSpec['dims'],np.int64)
        else:
            inputsData[inpSpec['name']] = np.ones(inpSpec['dims'],np.float32)
    # with tempfile.NamedTemporaryFile(suffix='.csv') as profile_file:
    #     onnx_tool.model_profile(model, dynamic_shapes=inputsData, savenode=profile_file.name)
    #     data = pd.read_csv(profile_file.name)
    #     print(data)
    #     macs = data.iloc[-1]['MACs']
    
    try:
        g = Graph(model.graph)
        # g.graph_reorder()
        g.shape_infer(inputsData)
        g.profile()
        # replace output dims
        for i,inpSpec in enumerate(outputsSpec):
            if output_shapes is not None and i < len(output_shapes):
                inpSpec['dims'] = output_shapes[i]
            else:
                inpSpec['dims'] = g.tensormap[inpSpec['name']].shape        
        macs = int(g.macs)
    except:
        macs = int(0)
    return macs

def get_inputs_outputs(onnx_model):    
    inpNames = [inp.name for inp in onnx_model.graph.input]
    outNames = [inp.name for inp in onnx_model.graph.output]
    inputs = []
    for inp in [input_node for input_node in onnx_model.graph.input if input_node.name not in [init.name for init in onnx_model.graph.initializer]]:
        inputs.append(dict(
            type="vector",
            name=inp.name,
            dims=[d.dim_value for d in inp.type.tensor_type.shape.dim],
            dataType=data_type_map[inp.type.tensor_type.elem_type]
        ))
    outputs = []
    for inp in onnx_model.graph.output:
        outputs.append(dict(
            type="vector",
            name=inp.name,
            dims=[d.dim_value for d in inp.type.tensor_type.shape.dim],
            dataType=data_type_map[inp.type.tensor_type.elem_type]
        ))
    return inputs, outputs

def get_externals(model, path):
    externals = []
    for init in model.graph.initializer:
        for ext in init.external_data:
            if ext.key == 'location':
                externals += [ext.value]
    folder = Path(os.path.dirname(path))
    return list(set([str(folder/ext) for ext in externals]))

def create_model(payload, apiKey):
    # URL of the API endpoint
    url = f"https://peer-ai.com/gateway/models"
    # url = "http://127.0.0.1:5001/peer-ai-org/us-central1/gateway/gateway/models"
    # Set the content type header
    headers = {
        "Content-Type": "application/json",
        "x-api-key" : apiKey
    }
    # Send the POST request
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

import concurrent.futures



def upload_model(apiKey, path, name, description, input_shapes=None, output_shapes=None):
    onnx_model = onnx.load(path, None, False)    

    with open(path, 'rb') as f:
        h = cid_sha256_hash(f.read())
    
    size = 0
    dataURLs = []
    externals = get_externals(onnx_model, path)
    if len(externals) > 0:
        # upload main file
        filename = f"{h}/{h}.onnx"
        info = get_model_upload_url(filename, apiKey)
        if info['status'] == "existed":
            modelURL = info['url']
            size1 = int(info['size'])
        else:
            modelURL,size1 = upload_google_cloud(path, info)
        size += size1
        def upload_external(extpath):
            # upload external file
            filename = f"{h}/{os.path.basename(extpath)}"
            info = get_model_upload_url(filename, apiKey)
            if info['status'] == "existed":            
                dataURL = info['url']
                size1 = int(info['size'])
            else:
                dataURL,size1 = upload_google_cloud(extpath, info)
            return dataURL,size1
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            # Upload external files in parallel
            futures = [executor.submit(upload_external, extpath) for extpath in externals]
            dataURLsSizes = [future.result() for future in concurrent.futures.as_completed(futures)]
            dataURLs = [res[0] for res in dataURLsSizes]
            size += sum([res[1] for res in dataURLsSizes])
    else:
        # upload main file
        filename = f"{h}.onnx"
        info = get_model_upload_url(filename, apiKey)
        if info['status'] == "existed":            
            modelURL = info['url']
            size1 = int(info['size'])
        else:
            modelURL,size1 = upload_google_cloud(path, info)
        size += size1

    inputs, outputs = get_inputs_outputs(onnx_model)
    modelFormat = 'ONNX' + ' v' + str(onnx_model.ir_version)
    if len(externals) > 0:
        onnx_model = onnx.load(path, None, True)   
    macs=get_macs(onnx_model, inputs, outputs, input_shapes, output_shapes)

    modelData = dict(
        inputs=inputs,
        outputs=outputs,
        modelURL=modelURL,
        dataURLs=dataURLs,
        hash=h,
        name=name,
        description=description,
        modelFormat=modelFormat,
        macs=macs,
        size=size
    )
    print(json.dumps(modelData))
    
    # post to api
    return create_model(modelData, apiKey)


def dynamic_quantize(model_fp32, model_quant):
    quantized_model = quantize_dynamic(model_fp32, model_quant)
    return quantized_model