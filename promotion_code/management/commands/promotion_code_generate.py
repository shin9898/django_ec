from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.utils import IntegrityError
import random, string

from promotion_code.models import PromotionCode

class Command(BaseCommand):
    help = '10個のプロモーションコードを生成します。'

    def handle(self, *args, **kwargs):
        generated_codes = []
        attempts = 0
        max_attempts_per_code = 10

        for _ in range(10):
            code_created = False
            for _attempt in range(max_attempts_per_code):
                code = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
                discount = random.randint(100, 1000)
                try:
                    with transaction.atomic():
                        PromotionCode.objects.create(code=code, discount=discount)
                    self.stdout.write(self.style.SUCCESS(f"プロモーションコード {code} ({discount}円割引)を生成しました。"))
                    generated_codes.append(f"{code} ({discount}円割引)")
                    code_created = True
                    break
                except IntegrityError:
                    self.stdout.write(self.style.WARNING(f"生成しようとしたコード {code} は既に存在します。再試行します..."))
                    continue
            if not code_created:
                self.stdout.write(self.style.ERROR(f"コード生成に失敗しました。 {max_attempts_per_code}回の施行後もユニークなコードを生成できませんでした。"))
                break

        self.stdout.write(self.style.SUCCESS('\n--- 生成されたプロモーションコード一覧 ---'))
        for c in generated_codes:
            self.stdout.write(self.style.SUCCESS(c))
        self.stdout.write(self.style.SUCCESS(f"計 {len(generated_codes)}個のプロモーションコードを生成しました。"))