import React, { act, useContext } from 'react';
import { fireEvent, render, renderHook, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Playground from '@/app/playground/playground';
import { PlaygroundProps } from '@/app/playground/playground';
import TrainButton from '@/app/playground/playground-components/left-sidebar/train_btn';
import '@testing-library/jest-dom';

import { TrainingFields } from '@/app/playground/contexts & popups/training_fields_ctx';
import NodeContainer from '@/app/playground/smallneuron-integration/sn_integration';
import { Edge } from 'reactflow';

import { Position } from 'react-flow-renderer';
import Output from '@/app/playground/playground-components/right-sidebar/train_losses';
import ForPassButton from '@/app/playground/playground-components/right-sidebar/fpass_btn';
import SelectionBox from '@/app/playground/playground-components/right-sidebar/dragndrop_box';
import ReinitBtn from '@/app/playground/playground-components/left-sidebar/reinit_btn';
import Hyper from '@/app/playground/playground-components/left-sidebar/hyper_parameters';
import LayronPopup from '@/app/playground/contexts & popups/layron_popup';
import LayerSelectionPopup from '@/app/playground/contexts & popups/layer_selection_popup';


// In your test file
global.ResizeObserver = jest.fn(() => ({
    observe: jest.fn(),
    unobserve: jest.fn(),
    disconnect: jest.fn(),
  }));

// Mock next/image to avoid fetchPriority warning
jest.mock('next/image', () => {
  const MockedImage = ({ src, alt, ...props }: { src: string, alt: string, props: any }) => (
      // eslint-disable-next-line @next/next/no-img-element
      <img src={src} alt={alt} {...props} />
  );
  MockedImage.displayName = 'NextImageMock';
  return MockedImage;
});

describe('Playground Component', () => {

    const props: PlaygroundProps = {
        isTrainingVisible: true,
        isHyperParamsVisible: true,
        isTrainBtnsVisible: true,
        isSelectionBoxVisible: true,
        isTrainLossVisible: true,
        isFPBtnVisible: true,
        trainingSets: []
    };

    test('renders all components when all visibility props are true', () => {
        render(<Playground {...props} />);

        

        expect(screen.getByText('Select a training set')).toBeInTheDocument(); // Training dropdown
        
        expect(screen.getByText('Epochs')).toBeInTheDocument(); // Hyperparameters
        expect(screen.getByRole('button', { name: 'TRAIN' })).toBeInTheDocument(); // Train button
        expect(screen.getByRole('button', { name: 'RE-INIT' })).toBeInTheDocument(); // Reinitialize button
        expect(screen.getByText('TRAINING LOSS')).toBeInTheDocument(); // Train losses output
        expect(screen.getByRole('button', { name: 'FORWARD PASS' })).toBeInTheDocument(); // Forward Pass button
        expect(screen.getByText('SELECTION BOX')).toBeInTheDocument(); // Selection Box
    });

});




describe('Smallneuron integration', () => {


  test('Testing for train, forwardpass, reinit, reset', () => {

      const mockNodes = [
          {
            id: 'i0',
            type: 'inputnode',
            sourcePosition: Position.Right,
            draggable: false,
            data: { label: 'IN 1', data: 0, index: 0 },
            position: { x: 0, y: 12 },
          },
          {
            id: 'n1',
            type: 'neuron',
            position: { x: 200, y: 12 },
            data: { label: 'neuron node', weight: 'uninitialized', bias: 'uninitialized' },
          },
          {
            id: 'o2',
            type: 'outputNeuron',
            targetPosition: Position.Left,
            draggable: true,
            selectable: false,
            data: {
              label: 'OUT 1',
              data: 0,
              weight: 'uninitialized',
              bias: 'uninitialized',
            },
            position: { x: 800, y: 12 },
          },
        ];
        
      const mockEdges = [
          { id: 'e0-1', source: 'i0', target: 'n1', type: 'smoothstep' },
          { id: 'e1-2', source: 'n1', target: 'o2', type: 'smoothstep' },
        ];
      

      const setLosses = jest.fn();

      const mockContextValue:TrainingFields = {
      
          Activation: 'relu', // Ensure this matches the expected type
          Epochs: 100,
          LearningRate: 0.01,
          BatchSize: 10,
      
          setActivation: jest.fn(),
          setEpochs: jest.fn(),
          setLearningRate: jest.fn(),
          setBatchSize: jest.fn(),
      
          TrainingState: 'train',
          setTrainingState: jest.fn(),
      
          Losses: [],
          setLosses: setLosses,
      
          TrainingData: {
            Inputs: [[1, 2], [3, 4]],
            Outputs: [[0.5], [0.8]],
          },
          setTrainingData: jest.fn(),
          
          isNewModel: true,
          setIsNewModel: jest.fn(),
      
          showFPData: [false, false],
          setShowFPData: jest.fn(),
          
      
          DatasetId: 0,
          setDatasetId: jest.fn(),
        };
    const {rerender} = render(
      <TrainingFields.Provider value={mockContextValue}>
        <NodeContainer
          nodes={mockNodes}
          edges={mockEdges}
          setNodes={jest.fn()}
          setEdges={jest.fn()}
        />
      </TrainingFields.Provider>
    );


    expect(setLosses).toHaveBeenCalled();

    mockContextValue.TrainingState = 'forpass';

    rerender(
      <TrainingFields.Provider value={mockContextValue}>
        <NodeContainer nodes={[]} edges={[]} setNodes={jest.fn()} setEdges={jest.fn()} />
      </TrainingFields.Provider>
    );

    expect(setLosses).toHaveBeenCalledWith(expect.any(Array<Number>));

    mockContextValue.TrainingState = 'reinit';

    rerender(
      <TrainingFields.Provider value={mockContextValue}>
        <NodeContainer nodes={[]} edges={[]} setNodes={jest.fn()} setEdges={jest.fn()} />
      </TrainingFields.Provider>
    );

    expect(mockContextValue.setIsNewModel).toHaveBeenCalledWith(true);

    mockContextValue.TrainingState = 'reset';

    rerender(
      <TrainingFields.Provider value={mockContextValue}>
        <NodeContainer nodes={[]} edges={[]} setNodes={jest.fn()} setEdges={jest.fn()} />
      </TrainingFields.Provider>
    );

    expect(mockContextValue.setIsNewModel).toHaveBeenCalledWith(true);

  });


  test('Testing for layer dropped and trycatches', () => {

      const mockNodes = [
          {
            id: 'layer1',
            type: 'layer',
            position: { x: 200, y: 12 },
            data: { label: 'layer node', weight: 'uninitialized', bias: 'uninitialized', input_width: 1, output_width: 1 },
          },
          {
              id: 'popup1',
              type: 'popup',
              data: { weight: 'some_weight', bias: 'some_bias', selectedNodeId: 'layer1' },
              position: { x: 300, y: 100 },
              draggable: false,
            },
        ];

        const mockEdges:Edge[] = [];

        const mockContextValue:TrainingFields = {
      
          Activation: 'relu', // Ensure this matches the expected type
          Epochs: 100,
          LearningRate: 0.01,
          BatchSize: 10,
      
          setActivation: jest.fn(),
          setEpochs: jest.fn(),
          setLearningRate: jest.fn(),
          setBatchSize: jest.fn(),
      
          TrainingState: 'train',
          setTrainingState: jest.fn(),
      
          Losses: [],
          setLosses: jest.fn(),
      
          TrainingData: {
            Inputs: [[1, 2], [3, 4]],
            Outputs: [[0.5], [0.8]],
          },
          setTrainingData: jest.fn(),
          
          isNewModel: true,
          setIsNewModel: jest.fn(),
      
          showFPData: [false, false],
          setShowFPData: jest.fn(),
          
      
          DatasetId: 0,
          setDatasetId: jest.fn(),
        };


      const {rerender} = render(
          <TrainingFields.Provider value={mockContextValue}>
          <NodeContainer
              nodes={mockNodes}
              edges={mockEdges}
              setNodes={jest.fn()}
              setEdges={jest.fn()}
          />
          </TrainingFields.Provider>
      );

      expect(mockContextValue.isNewModel).toBe(true);
      mockContextValue.TrainingState = 'forpass';

      rerender(<TrainingFields.Provider value={mockContextValue}>
          <NodeContainer
              nodes={mockNodes}
              edges={mockEdges}
              setNodes={jest.fn()}
              setEdges={jest.fn()}
          />
          </TrainingFields.Provider>);

      expect(mockContextValue.isNewModel).toBe(true);     

  })

  
});



describe('Training Loss and FP Button', () => {

  const mockContextValue:TrainingFields = {
      
      Activation: 'relu', // Ensure this matches the expected type
      Epochs: 100,
      LearningRate: 0.01,
      BatchSize: 10,
  
      setActivation: jest.fn(),
      setEpochs: jest.fn(),
      setLearningRate: jest.fn(),
      setBatchSize: jest.fn(),
  
      TrainingState: 'train',
      setTrainingState: jest.fn(),
  
      Losses: [0.1, 0.2, 0.3],
      setLosses: jest.fn(),
  
      TrainingData: {
        Inputs: [[1, 2], [3, 4]],
        Outputs: [[0.5], [0.8]],
      },
      setTrainingData: jest.fn(),
      
      isNewModel: true,
      setIsNewModel: jest.fn(),
  
      showFPData: [false, false],
      setShowFPData: jest.fn(),
      
  
      DatasetId: 0,
      setDatasetId: jest.fn(),
    };

  
  test('training loss', () => {
      
      const {rerender} = render(
        <TrainingFields.Provider value={mockContextValue}>
          <Output />
        </TrainingFields.Provider>
      );
  
      expect(screen.getByText('TRAINING LOSS')).toBeInTheDocument();
      expect(screen.getByText('0.30')).toBeInTheDocument();

      mockContextValue.Losses = [];

      rerender(
          <TrainingFields.Provider value={mockContextValue}>
            <Output />
          </TrainingFields.Provider>
        );
    
        expect(screen.getByText('TRAINING LOSS')).toBeInTheDocument();
        expect(screen.queryByText(/[\d.]+/)).toBeNull(); // no numeric value is present



    });


  test('renders button with correct text', () => {

    render(
      <TrainingFields.Provider value={mockContextValue}>
        <ForPassButton />
      </TrainingFields.Provider>
    );

    expect(screen.getByText('FORWARD PASS')).toBeInTheDocument();
  

    fireEvent.click(screen.getByText('FORWARD PASS'));

    expect(mockContextValue.setTrainingState).toHaveBeenCalledWith('forpass');
  });

});


describe('SelectionBox component', () => {
  test('renders selection box with correct title and description', () => {
    render(<SelectionBox />);
    expect(screen.getByText('SELECTION BOX')).toBeInTheDocument();
    expect(screen.getByText('You can add a new element to your canvas by dragging and dropping it.')).toBeInTheDocument();
  });

  test('renders neuron component with correct title', () => {
    render(<SelectionBox />);
    expect(screen.getByAltText('Neuron')).toBeInTheDocument();
    expect(screen.getByText('NEURON')).toBeInTheDocument();
  });

  test('renders neuron layer component with correct title', () => {
    render(<SelectionBox />);
    expect(screen.getByAltText('Neuron Layer')).toBeInTheDocument();
    expect(screen.getByText('NEURON LAYER')).toBeInTheDocument();
  });

  test('calls onDragStart function with correct nodeType when neuron is dragged', () => {
      const mockOnDragStart = jest.fn();
      render(<SelectionBox />);
      const neuronElement = screen.getByAltText('Neuron');
      fireEvent.dragStart(neuronElement, { dataTransfer: { setData: mockOnDragStart } });
      expect(mockOnDragStart).toHaveBeenCalledWith('application/reactflow', 'neuron');
    });

    test('calls onDragStart function with correct nodeType when neuron layer is dragged', () => {
      const mockOnDragStart = jest.fn();
      render(<SelectionBox />);
      const neuronLayerElement = screen.getByAltText('Neuron Layer');
      fireEvent.dragStart(neuronLayerElement, { dataTransfer: { setData: mockOnDragStart } });
      expect(mockOnDragStart).toHaveBeenCalledWith('application/reactflow', 'layer');
    });
});


describe('TrainButton component', () => {

  const mockContextValue:TrainingFields = {
      
      Activation: 'relu', // Ensure this matches the expected type
      Epochs: 100,
      LearningRate: 0.01,
      BatchSize: 10,
  
      setActivation: jest.fn(),
      setEpochs: jest.fn(),
      setLearningRate: jest.fn(),
      setBatchSize: jest.fn(),
  
      TrainingState: 'train',
      setTrainingState: jest.fn(),
  
      Losses: [],
      setLosses: jest.fn(),
  
      TrainingData: {
        Inputs: [[1, 2], [3, 4]],
        Outputs: [[0.5], [0.8]],
      },
      setTrainingData: jest.fn(),
      
      isNewModel: true,
      setIsNewModel: jest.fn(),
  
      showFPData: [false, false],
      setShowFPData: jest.fn(),
      
  
      DatasetId: 0,
      setDatasetId: jest.fn(),
    };

  test('renders "TRAIN" button when isNewModel is true', () => {

  const {rerender} = render(
  
      <TrainingFields.Provider value={mockContextValue}>
      <TrainButton />
      </TrainingFields.Provider>
  
  );

  expect(screen.getByText('TRAIN')).toBeInTheDocument();

  mockContextValue.isNewModel=false;

  rerender(<TrainingFields.Provider value={mockContextValue}>
      <TrainButton />
    </TrainingFields.Provider>)

  expect(screen.getByText('TRAIN FURTHER')).toBeInTheDocument();

  mockContextValue.isNewModel=true;

  rerender(<TrainingFields.Provider value={mockContextValue}>
      <TrainButton />
    </TrainingFields.Provider>);

  const trainButton = screen.getByText('TRAIN');
  fireEvent.click(trainButton);
  expect(mockContextValue.setTrainingState).toHaveBeenCalledWith('train');

  })


  test('calls setTrainingState function with "reinit" when button is clicked', () => {

      render(<TrainingFields.Provider value={mockContextValue}>
      <ReinitBtn />
    </TrainingFields.Provider>);
      const reinitButton = screen.getByText('RE-INIT');
      fireEvent.click(reinitButton);
      expect(mockContextValue.setTrainingState).toHaveBeenCalledWith('reinit');
  });

    


  test('Hyperparameters testing',() =>{
      render(<TrainingFields.Provider value={mockContextValue}>
          <Hyper />
        </TrainingFields.Provider>);

      const epochsInput = screen.getByLabelText('Epochs');
      fireEvent.change(epochsInput, { target: { value: '50' } });
      expect(mockContextValue.setEpochs).toHaveBeenCalledWith(50);


      render(<TrainingFields.Provider value={mockContextValue}>
          <Hyper />
        </TrainingFields.Provider>);

      const learningRateInput = screen.getByLabelText('Learning Rate');
      act( () => fireEvent.change(learningRateInput, { target: { value: '0.1' } }));
      expect(mockContextValue.setLearningRate).toHaveBeenCalledWith(0.1);


      render(<TrainingFields.Provider value={mockContextValue}>
          <Hyper />
        </TrainingFields.Provider>);
      const batchSizeInput = screen.getByLabelText('Batch Size');
      act( () => fireEvent.change(batchSizeInput, { target: { value: '20' } }));
      expect(mockContextValue.setBatchSize).toHaveBeenCalledWith(20);


      render(<TrainingFields.Provider value={mockContextValue}>
          <Hyper />
        </TrainingFields.Provider>);

      const activationLabels = screen.getAllByText('relu');
      expect(activationLabels.length).toBe(4);
      const activationDropdown = activationLabels[0].parentNode;
      
      expect(activationDropdown).not.toBeNull();
  })


});

describe('TrainingFields context', () => {
  test('setActivation updates Activation state', () => {
    const { result } = renderHook(() => useContext(TrainingFields));

    expect(result.current.Activation).toBe('relu');
    result.current.setActivation('relu');
    expect(result.current.Activation).toBe('relu');
  });

  test('setEpochs updates Epochs state', () => {
    const { result } = renderHook(() => useContext(TrainingFields));

    expect(result.current.Epochs).toBe(50);
    result.current.setEpochs(50);
    expect(result.current.Epochs).toBe(50);
  });

  test('setLearningRate updates LearningRate state', () => {
    const { result } = renderHook(() => useContext(TrainingFields));

    expect(result.current.LearningRate).toBe(0.01);
    result.current.setLearningRate(0.01);
    expect(result.current.LearningRate).toBe(0.01);
  });

  test('setBatchSize updates BatchSize state', () => {
    const { result } = renderHook(() => useContext(TrainingFields));

    expect(result.current.BatchSize).toBe(1);
    result.current.setBatchSize(1);
    expect(result.current.BatchSize).toBe(1);
  });

  test('setTrainingState updates TrainingState state', () => {
    const { result } = renderHook(() => useContext(TrainingFields));

    expect(result.current.TrainingState).toBe('idle');
    result.current.setTrainingState('idle');
    expect(result.current.TrainingState).toBe('idle');
  });

  test('setLosses updates Losses state', () => {
    const { result } = renderHook(() => useContext(TrainingFields));

    expect(result.current.Losses).toEqual([]);
    result.current.setLosses([]);
    expect(result.current.Losses).toEqual([]);
  });

  test('setTrainingData updates TrainingData state', () => {
    const { result } = renderHook(() => useContext(TrainingFields));
    const mockData = {
      Inputs: [[1, 2], [3, 4]],
      Outputs: [[0], [1]]
    };

    expect(result.current.TrainingData).toEqual({ Inputs: [], Outputs: [] });
    result.current.setTrainingData({ Inputs: [], Outputs: [] });
    expect(result.current.TrainingData).toEqual({ Inputs: [], Outputs: [] });
  });

  test('setIsNewModel updates isNewModel state', () => {
    const { result } = renderHook(() => useContext(TrainingFields));

    expect(result.current.isNewModel).toBe(true);
    result.current.setIsNewModel(true);
    expect(result.current.isNewModel).toBe(true);
  });

  test('setShowFPData updates showFPData state', () => {
    const { result } = renderHook(() => useContext(TrainingFields));

    expect(result.current.showFPData).toEqual([]);
    result.current.setShowFPData([]);
    expect(result.current.showFPData).toEqual([]);
  });

  test('setDatasetName updates DatasetName state', () => {
    const { result } = renderHook(() => useContext(TrainingFields));

    expect(result.current.DatasetId).toBe(0);
    result.current.setDatasetId(0);
    expect(result.current.DatasetId).toBe(0);
  });
});

describe('Contexts and popups', () => {

  const mockContextValue:TrainingFields = {
      
      Activation: 'relu', // Ensure this matches the expected type
      Epochs: 100,
      LearningRate: 0.01,
      BatchSize: 10,
  
      setActivation: jest.fn(),
      setEpochs: jest.fn(),
      setLearningRate: jest.fn(),
      setBatchSize: jest.fn(),
  
      TrainingState: 'train',
      setTrainingState: jest.fn(),
  
      Losses: [],
      setLosses: jest.fn(),
  
      TrainingData: {
        Inputs: [[1, 2], [3, 4]],
        Outputs: [[0.5], [0.8]],
      },
      setTrainingData: jest.fn(),
      
      isNewModel: true,
      setIsNewModel: jest.fn(),
  
      showFPData: [false, false],
      setShowFPData: jest.fn(),
      
  
      DatasetId: 0,
      setDatasetId: jest.fn(),
    };


  test('layron popup',() =>{

      render(
          <TrainingFields.Provider value={mockContextValue}>
            <LayronPopup data={{ weight: 0.5, bias: 0.2, selectedNodeId: 1 }} />
          </TrainingFields.Provider>
        );

  expect(screen.getByText('NEURON DETAILS')).toBeInTheDocument();
  expect(screen.getByText('Weights: Uninitialized')).toBeInTheDocument();
  expect(screen.getByText('Bias: Uninitialized')).toBeInTheDocument();

  });

  test('renders layer details with input and output width', () => {
      render(
        <TrainingFields.Provider value={mockContextValue}>
          <LayronPopup data={{ weight: 0.5, bias: 0.2, selectedNodeId: 1, input_width: 3, output_width: 5 }} />
        </TrainingFields.Provider>
      );
  
      expect(screen.getByText('LAYER DETAILS')).toBeInTheDocument();
      expect(screen.getByText('5 Neurons that take 3 inputs each')).toBeInTheDocument();
      expect(screen.getByText('Weights: Uninitialized')).toBeInTheDocument();
      expect(screen.getByText('Bias: Uninitialized')).toBeInTheDocument();
  
  });

  test('renders layer details with input and output width and uninitialized', () => {

    mockContextValue.isNewModel = false;

    render(
      <TrainingFields.Provider value={mockContextValue}>
        <LayronPopup data={{ weight: 0.5, bias: 0.2, selectedNodeId: 1, input_width: 3, output_width: 5 }} />
      </TrainingFields.Provider>
    );

    expect(screen.getByText('LAYER DETAILS')).toBeInTheDocument();
    expect(screen.getByText('5 Neurons that take 3 inputs each')).toBeInTheDocument();
    expect(screen.getByText('Weights: 0.5')).toBeInTheDocument();
    expect(screen.getByText('Bias: 0.2')).toBeInTheDocument();

  });

  test('renders correctly and calls onConfirm with input and output width', () => {
    const onConfirmMock = jest.fn();
    const xPos = 100;
    const yPos = 100;

    const { getByLabelText, getByText } = render(
      <LayerSelectionPopup xPos={xPos} yPos={yPos} onConfirm={onConfirmMock} />
    );

    const inputWidthInput = getByLabelText('Input Width:');
    const outputWidthInput = getByLabelText('Output Width:');

    fireEvent.change(inputWidthInput, { target: { value: '5' } });
    fireEvent.change(outputWidthInput, { target: { value: '10' } });

    fireEvent.click(getByText('Confirm'));

    expect(onConfirmMock).toHaveBeenCalledWith(5, 10);
  });


});

describe('LayerSelectionPopup component', () => {
  test('renders correctly and calls onConfirm with input and output width', () => {
    const onConfirmMock = jest.fn();
    const xPos = 100;
    const yPos = 100;

    const { getByLabelText, getByText } = render(
      <LayerSelectionPopup xPos={xPos} yPos={yPos} onConfirm={onConfirmMock} />
    );

    const inputWidthInput = getByLabelText('Input Width:') as HTMLInputElement;
    const outputWidthInput = getByLabelText('Output Width:') as HTMLInputElement;

    fireEvent.change(inputWidthInput, { target: { value: '5' } });
    fireEvent.change(outputWidthInput, { target: { value: '10' } });

    fireEvent.click(getByText('Confirm'));

    expect(onConfirmMock).toHaveBeenCalledWith(5, 10);
  });

  test('calls onConfirm with default width values when Confirm button is clicked without input', () => {
    const onConfirmMock = jest.fn();
    const xPos = 100;
    const yPos = 100;

    const { getByText } = render(
      <LayerSelectionPopup xPos={xPos} yPos={yPos} onConfirm={onConfirmMock} />
    );

    fireEvent.click(getByText('Confirm'));

    expect(onConfirmMock).toHaveBeenCalledWith(1, 1);
  });

  test('updates inputWidth state when input width changes', () => {
    const onConfirmMock = jest.fn();
    const xPos = 100;
    const yPos = 100;

    const { getByLabelText } = render(
      <LayerSelectionPopup xPos={xPos} yPos={yPos} onConfirm={onConfirmMock} />
    );

    const inputWidthInput = getByLabelText('Input Width:') as HTMLInputElement;

    fireEvent.change(inputWidthInput, { target: { value: '5' } });

    expect(inputWidthInput.value).toBe('5');
  });

  test('updates outputWidth state when output width changes', () => {
    const onConfirmMock = jest.fn();
    const xPos = 100;
    const yPos = 100;

    const { getByLabelText } = render(
      <LayerSelectionPopup xPos={xPos} yPos={yPos} onConfirm={onConfirmMock} />
    );

    const outputWidthInput = getByLabelText('Output Width:') as HTMLInputElement;

    fireEvent.change(outputWidthInput, { target: { value: '10' } });

    expect(outputWidthInput.value).toBe('10');
  });
});



  



