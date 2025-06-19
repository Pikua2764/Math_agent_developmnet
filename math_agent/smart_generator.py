import random
from collections import Counter, defaultdict
import logging
from .enhanced_similarity import EnhancedSimilarityChecker
from .generator import generate_problem
from .checker import check_problem
from .target import test_with_target
from .judge import judge_solution

logger = logging.getLogger(__name__)

class SmartGenerationController:
    def __init__(self):
        self.similarity_checker = EnhancedSimilarityChecker()
        self.generation_stats = defaultdict(lambda: {'attempts': 0, 'successes': 0, 'duplicates': 0})
        self.variation_intensity = 1.0
        
    def generate_problems_intelligently(self, number_of_valid_needed, pipeline, taxonomy_file, batch):
        """Intelligent generation that integrates with your existing system"""
        
        valid_count = 0
        attempt_count = 0
        max_attempts = number_of_valid_needed * 15  # Prevent infinite loops
        consecutive_failures = 0
        
        # Track topic distribution for diversity
        topic_distribution = Counter()
        
        logger.info(f"Starting intelligent generation of {number_of_valid_needed} problems")
        
        while valid_count < number_of_valid_needed and attempt_count < max_attempts:
            attempt_count += 1
            
            # Break if too many consecutive failures
            if consecutive_failures > 20:
                logger.warning("Too many consecutive failures, adjusting strategy")
                self.variation_intensity *= 1.5
                consecutive_failures = 0
            
            try:
                # Smart topic selection for diversity
                subject, topic = self.select_diverse_topic(
                    taxonomy_file, topic_distribution, number_of_valid_needed
                )
                
                # Create taxonomy dict for generator
                taxonomy = {"subject": subject, "topic": topic}
                
                # Generate problem with your existing system
                print(f"\nAttempt {attempt_count} - Generating {subject} - {topic}...")
                question, answer, hints, embedding, similar_problems = generate_problem(
                    pipeline['generator'], taxonomy=taxonomy
                )
                
                # Enhanced similarity check
                is_duplicate, dup_type, similarity_score, enhanced_similar = self.similarity_checker.enhanced_similarity_check(
                    question, subject, topic, embedding, similar_problems
                )
                
                if is_duplicate:
                    consecutive_failures += 1
                    self.generation_stats[f"{subject}|{topic}"]['duplicates'] += 1
                    logger.warning(f"Duplicate detected: {dup_type} (similarity: {similarity_score:.3f})")
                    continue
                
                # Continue with your existing validation pipeline
                print("Calling checker...")
                is_valid, rejection_reason, corrected_hints = check_problem(
                    question, answer, hints, pipeline['checker']
                )
                
                if not is_valid:
                    consecutive_failures += 1
                    print(f"Rejection reason: {rejection_reason}")
                    
                    # Create discarded problem (your existing logic)
                    from ..models import Problem
                    problem = Problem.objects.create(
                        subject=subject,
                        topic=topic,
                        question=question,
                        answer=answer,
                        hints=hints,
                        rejection_reason=rejection_reason,
                        status='discarded',
                        batch=batch,
                        problem_embedding=embedding,
                        similar_problems=similar_problems
                    )
                    self.update_similar_problems(problem, similar_problems)
                    continue
                
                # Use corrected hints if provided
                if corrected_hints:
                    hints = corrected_hints
                
                # Test with target (your existing logic)
                print("Calling target...")
                target_result = test_with_target(question, pipeline['target'])
                
                # Judge the solution (your existing logic)
                print("Calling judge...")
                is_solved = judge_solution(target_result, answer, pipeline['judge'])
                
                # Create successful problem
                status = 'solved' if is_solved else 'valid'
                from ..models import Problem
                problem = Problem.objects.create(
                    subject=subject,
                    topic=topic,
                    question=question,
                    answer=answer,
                    hints=hints,
                    status=status,
                    batch=batch,
                    problem_embedding=embedding,
                    similar_problems=similar_problems
                )
                self.update_similar_problems(problem, similar_problems)
                
                # Update counters
                topic_distribution[f"{subject}|{topic}"] += 1
                self.generation_stats[f"{subject}|{topic}"]['successes'] += 1
                consecutive_failures = 0
                
                if status == 'valid':
                    valid_count += 1
                    print(f"Valid problem count: {valid_count}/{number_of_valid_needed}")
                    
            except Exception as e:
                consecutive_failures += 1
                logger.error(f"Error in attempt {attempt_count}: {e}")
                continue
            
            # Adaptive strategy adjustment
            if attempt_count % 50 == 0:
                self.adjust_generation_strategy(valid_count, attempt_count)
        
        logger.info(f"Generation completed: {valid_count}/{number_of_valid_needed} in {attempt_count} attempts")
        return valid_count, attempt_count
    
    def select_diverse_topic(self, taxonomy_file, current_distribution, target_count):
        """Select topic to maintain diversity"""
        all_combinations = []
        for subject, topics in taxonomy_file.items():
            for topic in topics:
                all_combinations.append((subject, topic))
        
        # Weight selection based on current distribution
        weights = []
        for subject, topic in all_combinations:
            key = f"{subject}|{topic}"
            current_count = current_distribution[key]
            expected_count = target_count / len(all_combinations)
            
            # Prefer under-represented topics
            weight = max(0.1, expected_count - current_count + 1)
            
            # Reduce weight for topics with high duplicate rates
            duplicate_rate = self.generation_stats[key]['duplicates'] / max(1, self.generation_stats[key]['attempts'])
            weight *= (1 - min(0.8, duplicate_rate))
            
            weights.append(weight)
        
        # Weighted random selection
        selected_idx = random.choices(range(len(all_combinations)), weights=weights)[0]
        return all_combinations[selected_idx]
    
    def update_similar_problems(self, problem, similar_problems):
        """Update similar problems' relationships (your existing logic)"""
        for sim_id, sim_score in similar_problems.items():
            try:
                from ..models import Problem
                sim_prob = Problem.objects.get(id=sim_id)
                sim_dict = sim_prob.similar_problems or {}
                sim_dict[str(problem.id)] = sim_score
                sim_prob.similar_problems = sim_dict
                sim_prob.save(update_fields=['similar_problems'])
            except Problem.DoesNotExist:
                continue
    
    def adjust_generation_strategy(self, valid_count, total_attempts):
        """Adjust strategy based on success rate"""
        success_rate = valid_count / total_attempts if total_attempts > 0 else 0
        
        if success_rate < 0.2:
            self.variation_intensity = min(3.0, self.variation_intensity * 1.5)
            logger.warning(f"Low success rate: {success_rate:.2%}. Increasing variation.")
        elif success_rate > 0.6:
            self.variation_intensity = max(0.5, self.variation_intensity * 0.9)
            logger.info(f"Good success rate: {success_rate:.2%}.")