from math import sqrt

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

n = 115
a = 0
sigma = 9
np.random.seed(42)

# Part 1
print("=" * 60)
print("ЧАСТЬ I - НОРМАЛЬНОЕ РАСПРЕДЕЛЕНИЕ")
print("=" * 60)

print(f"Параметры: a = {a}, σ = {sigma}, n = {n}")
X = np.random.normal(a, sigma, n)
plt.plot(X, marker=".", linestyle="")
plt.show()
abs_freq, bin_edges = np.histogram(X, bins="sturges")

print("\n1.1. Интервальный ряд абсолютных частот:")
print("Интервал\t\tАбсолютная частота")
for i in range(len(abs_freq)):
    print(f"[{bin_edges[i]:.3f}, {bin_edges[i + 1]:.3f})\t\t{abs_freq[i]}")
total_abs_freq = np.sum(abs_freq)

print(f"\n1.2. Сумма абсолютных частот: {total_abs_freq}")
rel_freq, bin_edges_rel = np.histogram(X, bins="sturges", density=False)
rel_freq = rel_freq / n

print("\n1.3. Интервальный ряд относительных частот:")
print("Интервал\t\tОтносительная частота")
for i in range(len(rel_freq)):
    print(f"[{bin_edges_rel[i]:.3f},",
          f"{bin_edges_rel[i + 1]:.3f})\t\t{rel_freq[i]:.4f}")
total_rel_freq = np.sum(rel_freq)

print(f"\n1.4. Сумма относительных частот: {total_rel_freq:.6f}")

print("\n" + "=" * 60)
print("2. ВИЗУАЛИЗАЦИЯ ДАННЫХ")
print("=" * 60)
plt.figure(figsize=(15, 10))

plt.subplot(2, 3, 1)
for bins_count in range(2, 11):
    plt.hist(X, bins=bins_count, density=True, alpha=0.3, histtype="step")
plt.title("Гистограммы (2-10 интервалов)")
plt.xlabel("Значения")
plt.ylabel("Плотность")
plt.grid(True, alpha=0.3)

plt.subplot(2, 3, 2)
for bins_count in range(15, 26):
    plt.hist(X, bins=bins_count, density=True, alpha=0.3, histtype="step")
plt.title("Гистограммы (15-25 интервалов)")
plt.xlabel("Значения")
plt.ylabel("Плотность")
plt.grid(True, alpha=0.3)

plt.subplot(2, 3, 3)
plt.hist(X, bins=len(abs_freq), alpha=0.7, color="blue", edgecolor="black")
plt.title(f"Абсолютные частоты ({len(abs_freq)} интервалов)")
plt.xlabel("Значения")
plt.ylabel("Абсолютная частота")
plt.grid(True, alpha=0.3)

plt.subplot(2, 3, 4)
plt.hist(
    X,
    bins=len(abs_freq),
    density=True,
    alpha=0.7,
    color="lightblue",
    edgecolor="black",
    label="Эмпирическая",
)
x_theor = np.linspace(X.min(), X.max(), 1000)
y_theor = stats.norm.pdf(x_theor, a, sigma)
plt.plot(x_theor, y_theor, "r-", linewidth=2, label="Теоретическая")
plt.title("Относительные частоты + теоретическая кривая")
plt.xlabel("Значения")
plt.ylabel("Плотность")
plt.legend()
plt.grid(True, alpha=0.3)
modal_interval_idx = np.argmax(rel_freq)
modal_interval = (
    bin_edges_rel[modal_interval_idx],
    bin_edges_rel[modal_interval_idx + 1],
)
modal_freq = rel_freq[modal_interval_idx]
plt.axvspan(
    modal_interval[0],
    modal_interval[1],
    alpha=0.3,
    color="yellow",
    label=f"Модальный интервал\nЧастота: {modal_freq:.4f}",
)
plt.legend()

plt.subplot(2, 3, 5)
x_sorted = np.sort(X)
y_ecdf = np.arange(1, len(X) + 1) / len(X)
plt.hist(
    x_sorted,
    bins="sturges",
    density=True,
    cumulative=True,
    alpha=0.7,
    edgecolor="black",
    label="Эмпирическая ФР",
)
y_theor_cdf = stats.norm.cdf(x_theor, a, sigma)
plt.plot(x_theor, y_theor_cdf, "r-", label="Теоретическая ФР")
plt.title("Функции распределения")
plt.xlabel("Значения")
plt.ylabel("Вероятность")
plt.legend()
plt.grid(True, alpha=0.3)
plt.subplot(2, 3, 6)
plt.boxplot(X, vert=True)
plt.title("Бокс-плот распределения")
plt.ylabel("Значения")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
Q1 = np.percentile(X, 25)
Q2 = np.percentile(X, 50)
Q3 = np.percentile(X, 75)
IQR = Q3 - Q1
lower_whisker = Q1 - 1.5 * IQR
upper_whisker = Q3 + 1.5 * IQR
outliers = X[(X < lower_whisker) | (X > upper_whisker)]

print("\n2.5. Статистика бокс-плота:")
print(f"Q1 (25-й перцентиль): {Q1:.4f}")
print(f"Q2 (Медиана): {Q2:.4f}")
print(f"Q3 (75-й перцентиль): {Q3:.4f}")
print(f"IQR (интерквартильный размах): {IQR:.4f}")
print(f"Нижний ус: {lower_whisker:.4f}")
print(f"Верхний ус: {upper_whisker:.4f}")
print(f"Количество выбросов: {len(outliers)}")

print("\n" + "=" * 60)
print("3. ТОЧЕЧНОЕ ОЦЕНИВАНИЕ ПАРАМЕТРОВ")
print("=" * 60)


def manual_stats(data):
    n = len(data)
    mean = np.sum(data) / n
    variance = np.sum((data - mean) ** 2) / n
    corrected_variance = np.sum((data - mean) ** 2) / (n - 1)
    std = sqrt(variance)
    corrected_std = sqrt(corrected_variance)
    sorted_data = np.sort(data)
    if n % 2 == 0:
        median = (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
    else:
        median = sorted_data[n // 2]
    hist, bin_edges = np.histogram(data, bins="sturges")
    modal_bin_idx = np.argmax(hist)
    mode = (bin_edges[modal_bin_idx] + bin_edges[modal_bin_idx + 1]) / 2
    skewness = (np.sum((data - mean) ** 3) / n) / (std**3)
    kurtosis = (np.sum((data - mean) ** 4) / n) / (std**4) - 3
    return {
        "mean": mean,
        "median": median,
        "mode": mode,
        "variance": variance,
        "corrected_variance": corrected_variance,
        "std": std,
        "corrected_std": corrected_std,
        "skewness": skewness,
        "kurtosis": kurtosis,
    }


def builtin_stats(data):
    return {
        "mean": np.mean(data),
        "median": np.median(data),
        "mode": stats.mode(np.round(data)).mode,
        "variance": np.var(data),
        "corrected_variance": np.var(data, ddof=1),
        "std": np.std(data),
        "corrected_std": np.std(data, ddof=1),
        "skewness": stats.skew(data),
        "kurtosis": stats.kurtosis(data),
    }


manual_results = manual_stats(X)
builtin_results = builtin_stats(X)

print("3.1. СРАВНЕНИЕ МЕТОДОВ ОЦЕНИВАНИЯ:")
print("Параметр\t\tРучной способ\tВстроенные функции")
print("-" * 60)
for key in manual_results.keys():
    print(f"{key:15}\t{manual_results[key]:.6f}\t\t{builtin_results[key]:.6f}")

print("\n3.2. УВЕЛИЧЕНИЕ ОБЪЕМА ВЫБОРКИ В 60 РАЗ")
n_large = n * 60
X_large = np.random.normal(a, sigma, n_large)
large_results = builtin_stats(X_large)
print("Параметр\t\tИсходная выборка\tБольшая выборка\tТеоретическое")
print("-" * 80)
theoretical = {
    "mean": a,
    "median": a,
    "mode": a,
    "variance": sigma**2,
    "corrected_variance": sigma**2,
    "std": sigma,
    "corrected_std": sigma,
    "skewness": 0,
    "kurtosis": 0,
}
for key in builtin_results.keys():
    val1 = builtin_results[key]
    val2 = large_results[key]
    val3 = theoretical.get(key, 'N/A')
    print(f"{key:15}\t\t{val1:.6f}\t\t{val2:.6f}\t\t{val3:.6f}")

print("\n" + "=" * 60)
print("ОТВЕТЫ НА ВОПРОСЫ ЧАСТИ I")
print("=" * 60)

print("A) Анализ числа интервалов:")
print("Неоптимальные интервалы:")
print("- 2-4 интервала: слишком мало, теряем информацию о форме распределения")
print("- 20-25 интервалов: слишком много, появляется излишняя детализация")
print(f"Оптимальное число: {len(abs_freq)} интервалов (по правилу Стёрджеса)")
theoretical_prob = (stats.norm.cdf(modal_interval[1], a, sigma) -
                    stats.norm.cdf(modal_interval[0], a, sigma))

print(f"\nB) Модальный интервал: [{modal_interval[0]:.3f},",
      f"{modal_interval[1]:.3f})")
print(f"   Оценка вероятности: {modal_freq:.4f}")
print(f"   Теоретическая вероятность: {theoretical_prob:.4f}")
empirical_cdf_modal = len(X[X <= modal_interval[1]]) / len(X)
theoretical_cdf_modal = stats.norm.cdf(modal_interval[1], a, sigma)

print("\nC) Функция распределения в правой границе модального интервала:")
print(f"   Эмпирическая оценка: {empirical_cdf_modal:.4f}")
print(f"   Теоретическое значение: {theoretical_cdf_modal:.4f}")
theoretical_Q1 = stats.norm.ppf(0.25, a, sigma)
theoretical_Q3 = stats.norm.ppf(0.75, a, sigma)
theoretical_IQR = theoretical_Q3 - theoretical_Q1
theoretical_lower = theoretical_Q1 - 1.5 * theoretical_IQR
theoretical_upper = theoretical_Q3 + 1.5 * theoretical_IQR

print(f"\nD) Теоретические границы бокс-плота:")
print(f"   Q1 теоретический: {theoretical_Q1:.4f} (выборочный: {Q1:.4f})")
print(f"   Q3 теоретический: {theoretical_Q3:.4f} (выборочный: {Q3:.4f})")
print(
    f"   Нижний ус теоретический: {theoretical_lower:.4f}",
    f"(выборочный: {lower_whisker:.4f})"
)
print(
    f"   Верхний ус теоретический: {theoretical_upper:.4f}",
    f"(выборочный: {upper_whisker:.4f})"
)
print("   Отличия вызваны случайными флуктуациями в выборке")

# Part 2
print("\n" + "=" * 60)
print("ЧАСТЬ II - ТРЕУГОЛЬНОЕ РАСПРЕДЕЛЕНИЕ")
print("=" * 60)

left = -2
right = 4
mode = 1
k_interval = 3
epsilon = 0.006

print("Параметры треугольного распределения:")
print(f"  Левая граница: {left}")
print(f"  Правая граница: {right}")
print(f"  Мода: {mode}")
print(f"  Анализируемый интервал: {k_interval}")
print(f"  Точность ε: {epsilon}")
Y = np.random.triangular(left, mode, right, n)

print(f"\n1. Моделирование выборки Y ~ Triangle({left}, {mode}, {right})")
print(f"   Объем выборки: {n}")
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.hist(
    Y,
    bins=len(abs_freq),
    density=True,
    alpha=0.7,
    color="lightgreen",
    edgecolor="black",
    label="Эмпирическая",
)
x_theor_triang = np.linspace(left, right, 1000)
y_theor_triang = stats.triang.pdf(
    x_theor_triang,
    (mode - left) / (right - left),
    loc=left,
    scale=right - left
)
plt.plot(
    x_theor_triang,
    y_theor_triang,
    "r-",
    linewidth=2,
    label="Теоретическая"
)
plt.title("Треугольное распределение: гистограмма и теоретическая кривая")
plt.xlabel("Значения")
plt.ylabel("Плотность")
plt.legend()
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
plt.boxplot(Y, vert=True)
plt.title("Бокс-плот треугольного распределения Y")
plt.ylabel("Значения")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
Q1_Y = np.percentile(Y, 25)
Q3_Y = np.percentile(Y, 75)
IQR_Y = Q3_Y - Q1_Y
lower_whisker_Y = Q1_Y - 1.5 * IQR_Y
upper_whisker_Y = Q3_Y + 1.5 * IQR_Y
outliers_Y = Y[(Y < lower_whisker_Y) | (Y > upper_whisker_Y)]
triang_dist = stats.triang(
    (mode - left) / (right - left),
    loc=left,
    scale=right - left
)
theoretical_outlier_prob = triang_dist.cdf(lower_whisker_Y) + (
    1 - triang_dist.cdf(upper_whisker_Y)
)
theoretical_outliers_count = theoretical_outlier_prob * n

print("\n3. Статистика бокс-плота Y:")
print(f"   Q1: {Q1_Y:.4f}")
print(f"   Q3: {Q3_Y:.4f}")
print(f"   IQR: {IQR_Y:.4f}")
print(f"   Количество выбросов: {len(outliers_Y)}")
print(
    "   Теоретически ожидаемое количество выбросов:",
    f"{theoretical_outliers_count:.1f}"
)
Y_results = builtin_stats(Y)

print("\n4. Точечные оценки параметров Y:")
for key, value in Y_results.items():
    print(f"   {key:20}: {value:.6f}")
theoretical_mean_triang = (left + mode + right) / 3
theoretical_median_triang = triang_dist.median()
theoretical_var_triang = (
    left**2 + right**2 + mode**2 - left * right - left * mode - right * mode
) / 18

print("\n   Теоретические значения:")
print(f"   Среднее: {theoretical_mean_triang:.6f}")
print(f"   Медиана: {theoretical_median_triang:.6f}")
print(f"   Дисперсия: {theoretical_var_triang:.6f}")


def find_sample_size_triang(left, mode, right, epsilon=0.006, max_n=1000000):
    test_sizes = [100, 500, 1000, 5000, 10000, 50000, 100000, 500000, 1000000]
    triang_dist = stats.triang(
        (mode - left) / (right - left), loc=left, scale=right - left
    )
    for n_test in test_sizes:
        if n_test > max_n:
            break
        sample = np.random.triangular(left, mode, right, n_test)
        sample_sorted = np.sort(sample)
        ecdf = np.arange(1, n_test + 1) / n_test
        theoretical_cdf = triang_dist.cdf(sample_sorted)
        max_diff = np.max(np.abs(ecdf - theoretical_cdf))
        if max_diff <= epsilon:
            return n_test, max_diff
    return max_n, max_diff


optimal_n_triang, achieved_epsilon_triang = find_sample_size_triang(
    left, mode, right, epsilon
)

print("\n5. ПОДБОР ОБЪЕМА ВЫБОРКИ ДЛЯ ТРЕУГОЛЬНОГО РАСПРЕДЕЛЕНИЯ:")
print(f"   Целевая точность ε: {epsilon}")
print(f"   Найденный объем выборки: {optimal_n_triang}")
print(f"   Достигнутая точность: {achieved_epsilon_triang:.6f}")
Y_optimal = np.random.triangular(left, mode, right, optimal_n_triang)
plt.figure(figsize=(10, 6))
plt.hist(
    Y_optimal,
    bins=len(abs_freq),
    density=True,
    alpha=0.7,
    color="lightblue",
    edgecolor="black",
    label="Эмпирическая",
)
y_theor_opt = triang_dist.pdf(x_theor_triang)
plt.plot(x_theor_triang, y_theor_opt, "r-", linewidth=2, label="Теоретическая")
plt.title(
    f"Треугольное распределение (n={optimal_n_triang}, "
    f"ε={achieved_epsilon_triang:.6f})"
)
plt.xlabel("Значения")
plt.ylabel("Плотность")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

print("\n" + "=" * 60)
print("ОТВЕТЫ НА ВОПРОСЫ ЧАСТИ II")
print("=" * 60)

rel_freq_Y, bin_edges_Y = np.histogram(Y, bins=len(abs_freq), density=False)
rel_freq_Y = rel_freq_Y / len(Y)
if k_interval - 1 < len(rel_freq_Y):
    k_idx = k_interval - 1
    k_interval_prob = rel_freq_Y[k_idx]
    k_interval_range = (bin_edges_Y[k_idx], bin_edges_Y[k_idx + 1])
    k_theoretical_prob = (triang_dist.cdf(k_interval_range[1]) -
                          triang_dist.cdf(k_interval_range[0]))
    print(f"A) Вероятность попадания в {k_interval}-й интервал:")
    print(f"   Интервал: [{k_interval_range[0]:.3f},",
          f"{k_interval_range[1]:.3f})")
    print(f"   Оценка вероятности: {k_interval_prob:.4f}")

    print(f"B) Теоретическая вероятность: {k_theoretical_prob:.4f}")
    plt.figure(figsize=(8, 6))
    plt.hist(
        Y,
        bins=len(abs_freq),
        density=True,
        alpha=0.7,
        color="lightgray",
        edgecolor="black",
    )
    plt.axvspan(
        k_interval_range[0],
        k_interval_range[1],
        alpha=0.5,
        color="red",
        label=f"{k_interval}-й интервал\nВероятность: {k_interval_prob:.4f}",
    )
    plt.plot(
        x_theor_triang,
        y_theor_triang,
        "b-",
        linewidth=2,
        label="Теоретическая"
    )
    plt.title(f"{k_interval}-й интервал группировки")
    plt.xlabel("Значения")
    plt.ylabel("Плотность")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
else:
    print(
        f"Интервал {k_interval} выходит за пределы группировки",
        f"(всего {len(rel_freq_Y)} интервалов)"
    )
