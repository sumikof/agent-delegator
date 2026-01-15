"""
通信トポロジ管理

エージェント間の通信構造を管理
"""

import random
import math
from typing import Dict, List, Set, Any, Tuple
from dataclasses import dataclass


@dataclass
class CommunicationLink:
    """エージェント間の通信リンク"""
    source: str
    target: str
    bandwidth: float
    latency: float
    reliability: float


@dataclass
class CommunicationTopology:
    """通信トポロジ"""
    links: List[CommunicationLink]
    clusters: Dict[str, List[str]]  # cluster_id -> agent_ids


class CommunicationTopologyManager:
    """通信トポロジ管理システム"""
    
    def __init__(self):
        self.current_topology = CommunicationTopology(links=[], clusters={})
        self.agent_positions = {}  # agent_id -> (x, y) position for visualization
        
    def initialize_topology(self, agent_ids: List[str]) -> None:
        """初期トポロジを作成"""
        links = []
        clusters = {"default": agent_ids}
        
        # 簡単なメッシュトポロジを作成
        for i, agent_id in enumerate(agent_ids):
            # 隣接するエージェントと接続
            for j in range(i + 1, min(i + 3, len(agent_ids))):
                neighbor_id = agent_ids[j]
                links.append(CommunicationLink(
                    source=agent_id,
                    target=neighbor_id,
                    bandwidth=1.0,
                    latency=0.1,
                    reliability=0.95
                ))
        
        self.current_topology = CommunicationTopology(links=links, clusters=clusters)
        
        # エージェントの位置を初期化（視覚化用）
        for i, agent_id in enumerate(agent_ids):
            angle = 2 * math.pi * i / len(agent_ids)
            radius = 10.0
            self.agent_positions[agent_id] = (radius * math.cos(angle), radius * math.sin(angle))
    
    def optimize_topology(self, role_assignment: Dict[str, str], performance_data: Dict[str, Any]) -> CommunicationTopology:
        """トポロジを最適化"""
        # 現在のトポロジをコピー
        import copy
        new_topology = copy.deepcopy(self.current_topology)
        
        # 役割に基づいてクラスタリング
        self._cluster_by_roles(role_assignment, new_topology)
        
        # クラスター内の接続を強化
        self._strengthen_intra_cluster_connections(new_topology)
        
        # クラスター間の接続を最適化
        self._optimize_inter_cluster_connections(new_topology)
        
        # パフォーマンスに基づいてリンクを調整
        self._adjust_links_by_performance(performance_data, new_topology)
        
        return new_topology
    
    def _cluster_by_roles(self, role_assignment: Dict[str, str], topology: CommunicationTopology) -> None:
        """役割に基づいてクラスタリング"""
        role_clusters = {}
        
        # 役割ごとにエージェントをグループ化
        for agent_id, role in role_assignment.items():
            if role not in role_clusters:
                role_clusters[role] = []
            role_clusters[role].append(agent_id)
        
        # クラスターを更新
        topology.clusters = {}
        for role, agents in role_clusters.items():
            if len(agents) > 1:  # 2人以上のエージェントがいる場合にクラスターを作成
                topology.clusters[f"role_{role}"] = agents
    
    def _strengthen_intra_cluster_connections(self, topology: CommunicationTopology) -> None:
        """クラスター内の接続を強化"""
        # クラスター内のすべてのエージェントペアを接続
        for cluster_id, agents in topology.clusters.items():
            for i, agent_id in enumerate(agents):
                for j in range(i + 1, len(agents)):
                    neighbor_id = agents[j]
                    
                    # 既存のリンクを探す
                    existing_link = None
                    for link in topology.links:
                        if (link.source == agent_id and link.target == neighbor_id) or \
                           (link.source == neighbor_id and link.target == agent_id):
                            existing_link = link
                            break
                    
                    if existing_link:
                        # 既存のリンクを強化
                        existing_link.bandwidth = min(existing_link.bandwidth * 1.2, 2.0)
                        existing_link.latency = max(existing_link.latency * 0.9, 0.05)
                        existing_link.reliability = min(existing_link.reliability * 1.05, 0.99)
                    else:
                        # 新しいリンクを追加
                        topology.links.append(CommunicationLink(
                            source=agent_id,
                            target=neighbor_id,
                            bandwidth=1.5,
                            latency=0.08,
                            reliability=0.97
                        ))
    
    def _optimize_inter_cluster_connections(self, topology: CommunicationTopology) -> None:
        """クラスター間の接続を最適化"""
        cluster_ids = list(topology.clusters.keys())
        
        # クラスター間の接続を最適化
        for i, cluster_id1 in enumerate(cluster_ids):
            for j in range(i + 1, len(cluster_ids)):
                cluster_id2 = cluster_ids[j]
                
                # クラスター間の代表エージェントを選択
                rep1 = topology.clusters[cluster_id1][0]  # 簡略化：最初のエージェント
                rep2 = topology.clusters[cluster_id2][0]  # 簡略化：最初のエージェント
                
                # 既存のリンクを探す
                existing_link = None
                for link in topology.links:
                    if (link.source == rep1 and link.target == rep2) or \
                       (link.source == rep2 and link.target == rep1):
                        existing_link = link
                        break
                
                if existing_link:
                    # 既存のリンクを最適化
                    existing_link.bandwidth = min(existing_link.bandwidth * 1.1, 1.5)
                    existing_link.latency = max(existing_link.latency * 0.95, 0.1)
                else:
                    # 新しいリンクを追加
                    topology.links.append(CommunicationLink(
                        source=rep1,
                        target=rep2,
                        bandwidth=1.0,
                        latency=0.15,
                        reliability=0.92
                    ))
    
    def _adjust_links_by_performance(self, performance_data: Dict[str, Any], topology: CommunicationTopology) -> None:
        """パフォーマンスに基づいてリンクを調整"""
        # パフォーマンスデータに基づいてリンクを調整
        # 簡略化版：ランダムにリンクを調整
        for link in topology.links:
            # パフォーマンスが良い場合はリンクを強化
            if random.random() > 0.7:
                link.bandwidth = min(link.bandwidth * 1.05, 2.0)
                link.latency = max(link.latency * 0.98, 0.05)
            else:
                # パフォーマンスが悪い場合はリンクを弱化
                link.bandwidth = max(link.bandwidth * 0.98, 0.5)
                link.latency = min(link.latency * 1.02, 0.3)
    
    def get_communication_path(self, source: str, target: str) -> List[str]:
        """2つのエージェント間の通信パスを取得"""
        # 簡略化版：直接接続されている場合は直接パスを返す
        for link in self.current_topology.links:
            if (link.source == source and link.target == target) or \
               (link.source == target and link.target == source):
                return [source, target]
        
        # 直接接続されていない場合は、簡単なパスを探す
        # 実際の実装では、ダイクストラ法などのアルゴリズムを使用
        
        # 共通のクラスターを探す
        for cluster_id, agents in self.current_topology.clusters.items():
            if source in agents and target in agents:
                # 同じクラスター内の場合は、他のエージェントを経由
                for agent in agents:
                    if agent != source and agent != target:
                        return [source, agent, target]
        
        # デフォルト：直接接続
        return [source, target]
    
    def get_communication_cost(self, source: str, target: str) -> float:
        """2つのエージェント間の通信コストを取得"""
        path = self.get_communication_path(source, target)
        total_cost = 0.0
        
        for i in range(len(path) - 1):
            agent1 = path[i]
            agent2 = path[i + 1]
            
            # リンクを探す
            for link in self.current_topology.links:
                if (link.source == agent1 and link.target == agent2) or \
                   (link.source == agent2 and link.target == agent1):
                    # コスト = レイテンシ / バンド幅
                    cost = link.latency / link.bandwidth
                    total_cost += cost
                    break
        
        return total_cost
    
    def get_current_topology(self) -> CommunicationTopology:
        """現在のトポロジを取得"""
        return self.current_topology
    
    def update_topology(self, new_topology: CommunicationTopology) -> None:
        """トポロジを更新"""
        self.current_topology = new_topology
    
    def get_agent_positions(self) -> Dict[str, Tuple[float, float]]:
        """エージェントの位置を取得（視覚化用）"""
        return self.agent_positions
    
    def visualize_topology(self) -> Dict[str, Any]:
        """トポロジを視覚化用のデータとして取得"""
        nodes = []
        links = []
        
        # ノードデータを作成
        for agent_id, (x, y) in self.agent_positions.items():
            nodes.append({
                "id": agent_id,
                "x": x,
                "y": y
            })
        
        # リンクデータを作成
        for link in self.current_topology.links:
            links.append({
                "source": link.source,
                "target": link.target,
                "bandwidth": link.bandwidth,
                "latency": link.latency,
                "reliability": link.reliability
            })
        
        # クラスターデータを作成
        clusters = []
        for cluster_id, agents in self.current_topology.clusters.items():
            clusters.append({
                "id": cluster_id,
                "agents": agents
            })
        
        return {
            "nodes": nodes,
            "links": links,
            "clusters": clusters
        }