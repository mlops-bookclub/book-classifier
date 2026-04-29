# Baseline Recommender

## Model Type

- Item-item collaborative filtering


## Input and Split

- Dataset: `data/raw/goodbooks-10k/ratings.csv`
- Relevant columns:
  - `user_id`
  - `book_id`
  - `rating`
- Only ratings `4` and `5` are treated as positive interactions
- These interactions are converted into binary feedback:
  - `1` = user liked the book
  - `0` = no positive interaction
- Leave-one-out split per user:
  - the last positive interaction goes to test
  - the remaining positive ineractions go to train


## Step 1: Build a Binary User-Item Matrix

After filtering to ratings `4` and `5`, the model builds a binary matrix.

- Rows = users
- Columns = books
- Cell value `1` = user liked the book
- Cell value `0` = user did not positively interact with the book

Example:

```text
          Book A   Book B   Book C   Book D
User 1       1        1        0        0
User 2       1        0        1        0
User 3       0        1        1        1
```

## Step 2: Count Co-Likes Between Books

Two books are considered related if they were liked by the same users.

For each pair of books, the model counts how many users liked both.


```text
          Book A   Book B   Book C   Book D
Book A       -        1        1        0
Book B       1        -        1        1
Book C       1        1        -        1
Book D       0        1        1        -
```

## Step 3: Normalize the Co-Likes

because popular books would otherwise look "similar" to almost everything.

The model therefore normalizes each co-like count by the popularity of the two books .

First count how many users liked each book:

```text
Book A: 2 users
Book B: 2 users
Book C: 2 users
Book D: 1 user
```

Then compute similarity (cosine simliarity):

```text
sim(i, j) = co_likes(i, j) / sqrt(likes(i) * likes(j))
```

Example values:

```text
sim(A, B) = 1 / sqrt(2 * 2) = 1 / 2 = 0.50
sim(A, C) = 1 / sqrt(2 * 2) = 0.50
sim(B, D) = 1 / sqrt(2 * 1) = 0.71
sim(A, D) = 0 / sqrt(2 * 1) = 0.00
```

so:

- `0.00` = no shared liking behavior
- higher value = stronger similarity

## Step 4: Keep the Top Neighbors Per Book

After all similarities are computed:

- each book gets a list of similar books
- the list is sorted by similarity
- only the top `N` neighbors are kept

Current default:

```text
top_neighbors = 50
```
Internal structure:

```text
Book A -> [(Book B, 0.50), (Book C, 0.50)]
Book B -> [(Book D, 0.71), (Book A, 0.50), (Book C, 0.50)]
...
```

This is the fitted item-item neighborhood graph.


## Step 5: Prediction 

To recommend books for one user:

1. take the books from that user's history
2. look up the neighbors of each history book
3. ignore books already seen by the user
4. collect all unseen neighbor books as candidates
5. sum their similarity contributions
6. rank the candidates by total score
7. return the top `K`

Current default:

```text
top_k = 10
```

## Prediction Example

Assume a user has already liked:

```text
History = [Book A, Book B]
```

And the neighborhood lists are:

```text
Book A -> Book C (0.50), Book D (0.20)
Book B -> Book C (0.60), Book E (0.40)
```

Then the candidate scores become:

```text
Book C: 0.50 + 0.60 = 1.10
Book D: 0.20
Book E: 0.40
```

Ranked recommendations:

```text
1. Book C   score 1.10
2. Book E   score 0.40
3. Book D   score 0.20
```


## What Is Saved Currently

Currently, the pipeline saves metrics only, for example:

- `models/metrics/item_based_cf_baseline.json`

Saved fields include:

- `model`
- `ratings_path`
- `min_rating`
- `top_k`
- `top_neighbors`
- `train_interactions`
- `test_interactions`
- `num_users`
- `hit_rate_at_k`
- `recall_at_k`

## What Is Not Saved Currently

- No serialized recommender object
- No persisted item-item graph
- No saved user history
- No saved similarity matrix

## Output Locations

- Metrics folder:
  - [models/metrics](C:/Users/sv3nl/Documents/HSLU/MLOps/book-recommender/models/metrics)
- Baseline metrics file:
  - [item_based_cf_baseline.json](C:/Users/sv3nl/Documents/HSLU/MLOps/book-recommender/models/metrics/item_based_cf_baseline.json)
- Additional run output currently present:
  - [item_based_cf_baseline_top100.json](C:/Users/sv3nl/Documents/HSLU/MLOps/book-recommender/models/metrics/item_based_cf_baseline_top100.json)
