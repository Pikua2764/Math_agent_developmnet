from django.shortcuts import render, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from .models import Batch, Problem
from .utils.generator import generate_problem
from .utils.hinter import generate_hints
from .utils.checker import check_problem
from .utils.target import test_with_target
from .utils.judge import judge_solution
from datetime import datetime
import json
import random
from .utils.similarity_utils import SIMILARITY_THRESHOLD

# Create your views here.

class GenerateView(View):
    def get(self, request):
        return render(request, 'math_agent/generate.html')

    def post(self, request):
        try:
            # Get parameters from request
            number_of_valid_needed = int(request.POST.get('number_of_valid_needed'))
            pipeline = json.loads(request.POST.get('pipeline'))
            taxonomy_file = json.loads(request.FILES.get('taxonomy_file').read().decode('utf-8'))

            # Create new batch
            batch = Batch.objects.create(
                name=f"Batch_{pipeline['target']['model']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                taxonomy_json=taxonomy_file,
                pipeline=pipeline,
                number_of_valid_needed=number_of_valid_needed
            )

            valid_count = 0
            attempt_count = 0
            
            while valid_count < number_of_valid_needed:
                attempt_count += 1
                print(f"\nAttempt {attempt_count}")
                print("=" * 50)
                
                # Randomly select subject and topic from taxonomy
                subject = random.choice(list(taxonomy_file.keys()))
                topic = random.choice(taxonomy_file[subject])
                
                # Create taxonomy dict for generator
                taxonomy = {
                    "subject": subject,
                    "topic": topic
                }
                
                # Generate problem (now includes hints, embedding, similar_problems)
                print(f"Calling generator for {subject} - {topic}...")
                question, answer, hints, embedding, similar_problems = generate_problem(pipeline['generator'], taxonomy=taxonomy)
                print(f"Generator result:\nQuestion: {question}\nAnswer: {answer}\nHints: {json.dumps(hints, indent=2)}\nSimilar: {similar_problems}")
                
                # Check problem validity
                print("\nCalling checker...")
                is_valid, rejection_reason, corrected_hints = check_problem(question, answer, hints, pipeline['checker'])
                print(f"Checker result: {'Valid' if is_valid else 'Invalid'}")
                
                if not is_valid:
                    print(f"Rejection reason: {rejection_reason}")
                    # Create discarded problem
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
                    # Update similar problems' similar_problems field
                    for sim_id, sim_score in similar_problems.items():
                        try:
                            sim_prob = Problem.objects.get(id=sim_id)
                            sim_dict = sim_prob.similar_problems or {}
                            sim_dict[str(problem.id)] = sim_score
                            sim_prob.similar_problems = sim_dict
                            sim_prob.save(update_fields=['similar_problems'])
                        except Problem.DoesNotExist:
                            continue
                    continue
                
                # Use corrected hints if provided
                if corrected_hints:
                    print("Using corrected hints from checker")
                    hints = corrected_hints

                # Test with target
                print("\nCalling target...")
                target_result = test_with_target(question, pipeline['target'])
                print(f"Target result:\n{target_result}")
                
                # Judge the solution
                print("\nCalling judge...")
                is_solved = judge_solution(target_result, answer, pipeline['judge'])
                print(f"Judge result: {'Solved' if is_solved else 'Not Solved'}")
                
                # Create problem with appropriate status
                status = 'solved' if is_solved else 'valid'
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
                # Update similar problems' similar_problems field
                for sim_id, sim_score in similar_problems.items():
                    try:
                        sim_prob = Problem.objects.get(id=sim_id)
                        sim_dict = sim_prob.similar_problems or {}
                        sim_dict[str(problem.id)] = sim_score
                        sim_prob.similar_problems = sim_dict
                        sim_prob.save(update_fields=['similar_problems'])
                    except Problem.DoesNotExist:
                        continue
                
                if status == 'valid':
                    valid_count += 1
                    print(f"\nValid problem count: {valid_count}/{number_of_valid_needed}")

            return JsonResponse({
                'status': 'success',
                'batch_id': batch.id,
                'message': f'Successfully generated batch with {valid_count} valid problems in {attempt_count} attempts'
            })

        except Exception as e:
            print(f"\nError occurred: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

class BatchListView(ListView):
    model = Batch
    template_name = 'math_agent/batches.html'
    context_object_name = 'batches'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for batch in context['batches']:
            batch.stats = {
                'discarded': batch.problems.filter(status='discarded').count(),
                'solved': batch.problems.filter(status='solved').count(),
                'valid': batch.problems.filter(status='valid').count()
            }
        return context

class BatchDetailView(DetailView):
    model = Batch
    template_name = 'math_agent/batch_detail.html'
    context_object_name = 'batch'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stats'] = {
            'discarded': self.object.problems.filter(status='discarded').count(),
            'solved': self.object.problems.filter(status='solved').count(),
            'valid': self.object.problems.filter(status='valid').count()
        }
        return context

class ProblemDetailView(DetailView):
    model = Problem
    template_name = 'math_agent/problem_detail.html'
    context_object_name = 'problem'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add batch information
        context['batch'] = self.object.batch
        # Add similar problems queryset
        similar_ids = list(map(int, self.object.similar_problems.keys())) if self.object.similar_problems else []
        context['similar_problems'] = Problem.objects.filter(id__in=similar_ids) if similar_ids else []
        context['similarity_scores'] = self.object.similar_problems if self.object.similar_problems else {}
        return context

class ProblemListView(ListView):
    model = Problem
    template_name = 'math_agent/problems.html'
    context_object_name = 'problems'

    def get_queryset(self):
        queryset = Problem.objects.all()
        batch_id = self.kwargs.get('batch_id')
        status = self.request.GET.get('status')

        if batch_id:
            queryset = queryset.filter(batch_id=batch_id)
        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['batch_id'] = self.kwargs.get('batch_id')
        context['status'] = self.request.GET.get('status')
        return context

class AllProblemsView(ListView):
    model = Problem
    template_name = 'math_agent/all_problems.html'
    context_object_name = 'problems'

    def get_queryset(self):
        queryset = Problem.objects.all()
        status = self.request.GET.get('status')
        
        if status:
            queryset = queryset.filter(status=status)
            
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status'] = self.request.GET.get('status')
        return context
