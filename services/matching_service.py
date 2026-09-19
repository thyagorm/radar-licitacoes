"""
Serviço de matching inteligente
"""
import logging
from difflib import SequenceMatcher
from typing import Dict, List

logger = logging.getLogger(__name__)


class MatchingService:
    """Serviço para fazer matching entre portfolio e licitações"""
    
    MIN_THRESHOLD = 0.6  # Score mínimo para considerar um match
    
    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """
        Calcula similaridade entre dois textos usando SequenceMatcher
        
        Args:
            text1: Primeiro texto
            text2: Segundo texto
        
        Returns:
            Score entre 0 e 1
        """
        if not text1 or not text2:
            return 0.0
        
        matcher = SequenceMatcher(None, text1.lower(), text2.lower())
        return matcher.ratio()
    
    @staticmethod
    def calculate_jaccard_similarity(keywords1: str, keywords2: str) -> float:
        """
        Calcula similaridade Jaccard entre conjuntos de keywords
        
        Args:
            keywords1: Keywords separadas por vírgula
            keywords2: Keywords separadas por vírgula
        
        Returns:
            Score entre 0 e 1
        """
        if not keywords1 or not keywords2:
            return 0.0
        
        set1 = set(keywords1.lower().split(","))
        set2 = set(keywords2.lower().split(","))
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def match_product_with_licitation(
        product: Dict,
        licitation_item: Dict
    ) -> Dict:
        """
        Faz matching entre um produto e um item de licitação
        
        Args:
            product: Dados do produto do portfolio
            licitation_item: Dados do item da licitação
        
        Returns:
            Dict com score, reason e dados do match
        """
        
        scores = []
        reasons = []
        
        # 1. CMED Exact Match (score 1.0)
        if product.get("code") and licitation_item.get("code_cmed"):
            if product.get("code").upper() == licitation_item.get("code_cmed").upper():
                scores.append(1.0)
                reasons.append("Código CMED coincide")
        
        # 2. NCM Exact Match (score 0.9)
        if product.get("code") and licitation_item.get("code_ncm"):
            if product.get("code").upper() == licitation_item.get("code_ncm").upper():
                scores.append(0.9)
                reasons.append("Código NCM coincide")
        
        # 3. Keywords Similarity (Jaccard)
        product_keywords = product.get("keywords", "")
        item_description = licitation_item.get("description", "")
        
        if product_keywords:
            keyword_score = MatchingService.calculate_jaccard_similarity(
                product_keywords,
                item_description
            )
            if keyword_score > 0:
                scores.append(keyword_score * 0.8)  # Peso menor para keywords
                reasons.append(f"Keywords match ({keyword_score:.0%})")
        
        # 4. Description Similarity (Text)
        product_desc = product.get("description", "")
        text_score = MatchingService.calculate_similarity(
            product_desc,
            item_description
        )
        
        if text_score > 0.3:
            scores.append(text_score * 0.7)  # Peso para texto
            reasons.append(f"Descrição similar ({text_score:.0%})")
        
        # 5. Category Match (adiciona pontos)
        if product.get("category") and licitation_item.get("category"):
            if product.get("category").lower() == licitation_item.get("category").lower():
                scores.append(0.8)
                reasons.append("Categoria coincide")
        
        # Calcular score final (média ponderada)
        final_score = (sum(scores) / len(scores)) * 100 if scores else 0
        
        return {
            "score": final_score,
            "reason": " | ".join(reasons) if reasons else "Nenhuma correspondência",
            "matched": final_score >= MatchingService.MIN_THRESHOLD * 100
        }
    
    @staticmethod
    def calculate_viability(
        product_cost: float,
        product_margin: float,
        licitation_value: float
    ) -> Dict:
        """
        Calcula viabilidade comercial
        
        Args:
            product_cost: Preço de custo do produto
            product_margin: Margem mínima esperada (%)
            licitation_value: Valor estimado da licitação
        
        Returns:
            Dict com viabilidade e margem estimada
        """
        
        if not product_cost or not licitation_value:
            return {
                "viability": "média",
                "margin": None
            }
        
        # Calcular margem
        margin_percent = ((licitation_value - product_cost) / licitation_value) * 100
        
        # Classificar viabilidade
        if margin_percent >= product_margin * 1.5:
            viability = "alta"
        elif margin_percent >= product_margin:
            viability = "média"
        else:
            viability = "baixa"
        
        return {
            "viability": viability,
            "margin": round(margin_percent, 2)
        }


# Instância global
matching_service = MatchingService()
