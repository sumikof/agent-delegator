"""
量子コンピューティングバックエンドインターフェース

量子コンピューティングリソースとの接続と基本操作を提供
"""

import abc
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class QuantumBackend(abc.ABC):
    """
    量子コンピューティングバックエンドの抽象基底クラス
    
    具体的な量子コンピューティングプラットフォーム（IBM Quantum, Google Quantum AI, etc.）
    とのインターフェースを定義
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        量子バックエンドを初期化
        
        Args:
            config: 量子バックエンドの設定
        """
        self.config = config or {}
        self._initialized = False
        
    @abc.abstractmethod
    def initialize(self) -> bool:
        """
        量子バックエンドを初期化
        
        Returns:
            初期化が成功したかどうか
        """
        pass
        
    @abc.abstractmethod
    def execute_circuit(self, circuit: Any, shots: int = 1024) -> Dict[str, Any]:
        """
        量子回路を実行
        
        Args:
            circuit: 実行する量子回路
            shots: 実行回数（デフォルト: 1024）
            
        Returns:
            実行結果
        """
        pass
        
    @abc.abstractmethod
    def get_backend_info(self) -> Dict[str, Any]:
        """
        量子バックエンドの情報を取得
        
        Returns:
            バックエンド情報
        """
        pass
        
    @abc.abstractmethod
    def is_available(self) -> bool:
        """
        量子バックエンドが利用可能かどうかを確認
        
        Returns:
            利用可能かどうか
        """
        pass
        
    def __enter__(self):
        """コンテキストマネージャーのエントリーポイント"""
        if not self._initialized:
            self.initialize()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャーのエグジットポイント"""
        self.cleanup()
        
    def cleanup(self):
        """リソースのクリーンアップ"""
        pass


class QiskitBackend(QuantumBackend):
    """
    IBM Quantum (Qiskit) バックエンドの実装
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._backend = None
        self._provider = None
        
    def initialize(self) -> bool:
        """
        Qiskitバックエンドを初期化
        """
        try:
            # Qiskitのインポートと初期化
            from qiskit import IBMQ
            from qiskit.providers.ibmq import least_busy
            
            # IBM Quantumアカウントのロード
            IBMQ.load_account()
            self._provider = IBMQ.get_provider(hub=self.config.get('hub'), 
                                             group=self.config.get('group'), 
                                             project=self.config.get('project'))
            
            # 最も空いているバックエンドを選択
            large_enough_devices = self._provider.backends(
                filters=lambda x: x.configuration().n_qubits >= self.config.get('min_qubits', 5) 
                and not x.configuration().simulator
            )
            self._backend = least_busy(large_enough_devices)
            
            logger.info(f"Qiskit backend initialized: {self._backend.name()}")
            self._initialized = True
            return True
            
        except ImportError:
            logger.error("Qiskit is not installed. Please install qiskit package.")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Qiskit backend: {e}")
            return False
            
    def execute_circuit(self, circuit: Any, shots: int = 1024) -> Dict[str, Any]:
        """
        Qiskitを使用して量子回路を実行
        """
        if not self._initialized:
            if not self.initialize():
                raise RuntimeError("Quantum backend is not initialized")
                
        try:
            from qiskit import execute
            
            # 量子回路を実行
            job = execute(circuit, backend=self._backend, shots=shots)
            result = job.result()
            
            # 結果を辞書形式に変換
            counts = result.get_counts()
            return {
                'counts': counts,
                'backend': self._backend.name(),
                'shots': shots,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Failed to execute quantum circuit: {e}")
            return {
                'error': str(e),
                'success': False
            }
            
    def get_backend_info(self) -> Dict[str, Any]:
        """
        Qiskitバックエンドの情報を取得
        """
        if not self._backend:
            return {'error': 'Backend not initialized', 'available': False}
            
        return {
            'name': self._backend.name(),
            'status': self._backend.status().status_msg,
            'qubits': self._backend.configuration().n_qubits,
            'available': self._backend.status().operational,
            'pending_jobs': self._backend.status().pending_jobs
        }
        
    def is_available(self) -> bool:
        """
        Qiskitバックエンドが利用可能かどうかを確認
        """
        if not self._backend:
            return False
        return self._backend.status().operational


class QuantumSimulatorBackend(QuantumBackend):
    """
    量子シミュレーターバックエンドの実装（開発環境用）
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._backend = None
        
    def initialize(self) -> bool:
        """
        量子シミュレーターバックエンドを初期化
        """
        try:
            from qiskit import Aer
            
            # シミュレーターの選択
            simulator_name = self.config.get('simulator', 'qasm_simulator')
            self._backend = Aer.get_backend(simulator_name)
            
            logger.info(f"Quantum simulator initialized: {simulator_name}")
            self._initialized = True
            return True
            
        except ImportError:
            logger.error("Qiskit is not installed. Please install qiskit package.")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize quantum simulator: {e}")
            return False
            
    def execute_circuit(self, circuit: Any, shots: int = 1024) -> Dict[str, Any]:
        """
        量子シミュレーターを使用して量子回路を実行
        """
        if not self._initialized:
            if not self.initialize():
                raise RuntimeError("Quantum backend is not initialized")
                
        try:
            from qiskit import execute
            
            # 量子回路を実行
            job = execute(circuit, backend=self._backend, shots=shots)
            result = job.result()
            
            # 結果を辞書形式に変換
            counts = result.get_counts()
            return {
                'counts': counts,
                'backend': f"simulator_{self._backend.name()}",
                'shots': shots,
                'success': True,
                'simulated': True
            }
            
        except Exception as e:
            logger.error(f"Failed to execute quantum circuit: {e}")
            return {
                'error': str(e),
                'success': False
            }
            
    def get_backend_info(self) -> Dict[str, Any]:
        """
        量子シミュレーターバックエンドの情報を取得
        """
        if not self._backend:
            return {'error': 'Backend not initialized', 'available': False}
            
        return {
            'name': f"simulator_{self._backend.name()}",
            'type': 'simulator',
            'available': True,
            'simulated': True
        }
        
    def is_available(self) -> bool:
        """
        量子シミュレーターバックエンドが利用可能かどうかを確認
        """
        return self._initialized


def get_quantum_backend(backend_type: str = 'simulator', config: Optional[Dict[str, Any]] = None) -> QuantumBackend:
    """
    量子バックエンドを取得
    
    Args:
        backend_type: バックエンドのタイプ ('simulator', 'qiskit', etc.)
        config: バックエンドの設定
        
    Returns:
        量子バックエンドのインスタンス
    """
    if backend_type == 'simulator':
        return QuantumSimulatorBackend(config)
    elif backend_type == 'qiskit':
        return QiskitBackend(config)
    else:
        raise ValueError(f"Unknown quantum backend type: {backend_type}")