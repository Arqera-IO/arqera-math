"""Game Theory Service.

Provides game-theoretic mechanisms for resource conflict resolution:
- Priority-based auctions for file/resource locks
- Nash equilibrium approximation for multi-agent scenarios
- Fair resource allocation

Standalone -- no SQLAlchemy or external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


@dataclass
class ResourceClaim:
    """A claim by an agent for a resource."""

    claim_id: str = field(default_factory=lambda: str(uuid4()))
    agent_id: str = ""
    resource_id: str = ""
    resource_type: str = "file"
    urgency: float = 0.5
    importance: float = 0.5
    agent_reputation: float = 1.0
    score: float = 0.0
    claimed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "claim_id": self.claim_id,
            "agent_id": self.agent_id,
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "urgency": self.urgency,
            "importance": self.importance,
            "agent_reputation": self.agent_reputation,
            "score": self.score,
            "claimed_at": self.claimed_at.isoformat(),
        }


@dataclass
class AuctionResult:
    """Result of a resource auction."""

    auction_id: str = field(default_factory=lambda: str(uuid4()))
    resource_id: str = ""
    winner: ResourceClaim | None = None
    participants: list[ResourceClaim] = field(default_factory=list)
    auction_type: str = "priority_score"
    reasoning: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "auction_id": self.auction_id,
            "resource_id": self.resource_id,
            "winner": self.winner.to_dict() if self.winner else None,
            "participants_count": len(self.participants),
            "auction_type": self.auction_type,
            "reasoning": self.reasoning,
            "created_at": self.created_at.isoformat(),
        }


class ResourceAuction:
    """Auction-based resource conflict resolution.

    Implements a priority scoring auction mechanism:
    - Each agent submits a claim with urgency, importance, and reputation
    - Claims are scored using weighted combination
    - Highest score wins the resource

    Scoring formula:
    score = urgency x 0.4 + importance x 0.35 + reputation x 0.25
    """

    URGENCY_WEIGHT = 0.4
    IMPORTANCE_WEIGHT = 0.35
    REPUTATION_WEIGHT = 0.25

    def compute_claim_score(self, claim: ResourceClaim) -> float:
        """Compute priority score for a claim."""
        score = (
            claim.urgency * self.URGENCY_WEIGHT
            + claim.importance * self.IMPORTANCE_WEIGHT
            + claim.agent_reputation * self.REPUTATION_WEIGHT
        )
        claim.score = score
        return score

    def resolve_conflict(
        self,
        claims: list[ResourceClaim],
        resource_id: str = "",
    ) -> AuctionResult:
        """Resolve conflict between multiple claims using priority auction.

        Args:
            claims: List of claims for the same resource
            resource_id: ID of the contested resource

        Returns:
            AuctionResult with the winning claim
        """
        reasoning: list[str] = []

        if not claims:
            return AuctionResult(
                resource_id=resource_id,
                winner=None,
                reasoning=["No claims to process"],
            )

        if len(claims) == 1:
            claims[0].score = self.compute_claim_score(claims[0])
            return AuctionResult(
                resource_id=resource_id,
                winner=claims[0],
                participants=claims,
                reasoning=["Single claim - automatic winner"],
            )

        reasoning.append(f"Resolving conflict between {len(claims)} claims")

        # Compute scores for all claims
        for claim in claims:
            score = self.compute_claim_score(claim)
            reasoning.append(
                f"  Agent {claim.agent_id}: urgency={claim.urgency:.2f}, "
                f"importance={claim.importance:.2f}, "
                f"reputation={claim.agent_reputation:.2f} "
                f"-> score={score:.3f}"
            )

        # Sort by score descending
        sorted_claims = sorted(claims, key=lambda c: c.score, reverse=True)

        winner = sorted_claims[0]
        reasoning.append(f"Winner: Agent {winner.agent_id} with score {winner.score:.3f}")

        # Check for ties (within 0.01)
        if len(sorted_claims) > 1:
            second = sorted_claims[1]
            if abs(winner.score - second.score) < 0.01:
                reasoning.append(
                    f"Near-tie with Agent {second.agent_id} (score {second.score:.3f})"
                )
                if second.claimed_at < winner.claimed_at:
                    winner = second
                    reasoning.append(f"Tiebreaker: Agent {winner.agent_id} claimed earlier")

        return AuctionResult(
            resource_id=resource_id,
            winner=winner,
            participants=sorted_claims,
            auction_type="priority_score",
            reasoning=reasoning,
        )

    def compute_social_welfare(self, result: AuctionResult) -> float:
        """Compute social welfare of an auction result."""
        if not result.participants:
            return 0.0

        total = 0.0
        for claim in result.participants:
            if result.winner and claim.claim_id == result.winner.claim_id:
                total += claim.score
            else:
                total += claim.score * 0.2
        return total

    def is_pareto_optimal(self, result: AuctionResult) -> bool:
        """Check if auction result is Pareto optimal."""
        if not result.winner or not result.participants:
            return True
        max_score = max(c.score for c in result.participants)
        return result.winner.score == max_score


# =============================================================================
# Utility Functions
# =============================================================================


def create_claim(
    agent_id: str,
    resource_id: str,
    urgency: float = 0.5,
    importance: float = 0.5,
    reputation: float = 1.0,
    **kwargs: Any,
) -> ResourceClaim:
    """Helper to create a resource claim."""
    return ResourceClaim(
        agent_id=agent_id,
        resource_id=resource_id,
        urgency=max(0, min(1, urgency)),
        importance=max(0, min(1, importance)),
        agent_reputation=max(0, min(1, reputation)),
        metadata=kwargs,
    )
