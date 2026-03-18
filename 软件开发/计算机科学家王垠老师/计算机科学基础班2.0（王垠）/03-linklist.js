var show = (x) => console.log(x);
function pair(a, b)//构造函数
{
  return select => select(a, b);
}

var p1 = pair(2, 3);  // 创造一个新的 pair 结构，内容是 2 和 3。
var p1 = pair(2, 3);
// show(p1((a, b) => a * b));  // 会返回 6
// show(p1((a, b) => a + b));  // 会返回 5

function first(p)//访问函数
{
    return p((a, b) => a);
}

function second(p)//访问函数
{
    return p((a, b) => b);
}
function isPair(x)
{
    return typeof(x) == "function";
}

var p1 = pair(2, 3);
// show(first(p1));
// show(second(p1));
// show(isPair(p1));

function pairToString(x)
{
    if (! isPair(x))
    {
        return String(x);
    }
    else
    {
        return "("
        + pairToString(first(x))
        + ", "
        + pairToString(second(x))
        + ")";
    }
}
var p2 = pair(4, p1);
var p3 = pair(p2, null);
// show(pairToString(p1));
// show(pairToString(p2));
// show(pairToString(p3));

function length(ls)
{
    if (ls == null)
    {
        return 0;
    }
    else
    {
        return (1 + length(second(ls)));
    }
}

var ls1 = pair(2, null);
var ls2 = pair(2, pair(3, null));
var ls3 = pair(2, pair(3, pair(4, null)));
// show(length(ls1));
// show(length(ls2));
// show(length(ls3));

var head = first;
var tail = second;
function append(ls1, ls2)
{
    if (ls1 == null)
    {
        return ls2;
    }
    else
    {
        return pair(head(ls1), append(tail(ls1), ls2));
    }
}
// show(pairToString(ls1));
// show(pairToString(ls2));
// show(pairToString(ls3));
// show(pairToString(append(ls1, ls2)));
// show(pairToString(append(ls1, ls3)));

function nth(ls, n)
{
    if (ls == null)
    {
        throw "out of bound"
    }
    else if (n == 0)
    {
        return head(ls);
    }
    else
    {
        return nth(tail(ls), n - 1);
    }
}
var ls3 = pair(4, pair(pair(2, 3), pair(6, null)));
// show(pairToString(nth(ls3, 0)));// 4
// show(pairToString(nth(ls3, 1)));// (2, 3)
// show(pairToString(nth(ls3, 2)));// 6

function listLength(ls)
{
    if (ls == null)
    {
        return 0;
    }
    else
    {
        return 1 + listLength(second(ls));
    }
}
var p1 = pair(2, null);
var p2 = pair(2, pair(3, null));
// show(listLength(p1));//1
// show(listLength(p2));//2

function nthListNode(ls, n)
{
    if (n == 0)
    {
        return head(ls);
    }
    else if (ls == null)
    {
        throw "out of bound"
    }
    else
    {
        return nthListNode(second(ls), n - 1);
    }
}
var ls1 = pair(2, null);
var ls2 = pair(2, pair(3, null));
var ls3 = append(ls1, ls2);
// show(pairToString(ls3));//(2, (2, (3, null)))
// show(pairToString(nthListNode(ls3, 0)));//2
// show(pairToString(nthListNode(ls3, 1)));//2
// show(pairToString(nthListNode(ls3, 2)));//3


function last(ls)
{
    if (ls == null)
    {
        throw "list is null"
    }
    else if (second(ls) == null)
    {
        return first(ls);
    }
    else
    {
        return last(second(ls));
    }
}
var list1 = pair(7, pair(3, pair(2, pair(9, null))));
var list2 = pair(5, pair(4, pair(6, pair(1, pair(8, null)))));
// show(pairToString(list1));// (7, (3, (2, (9, null))))
// show(last(list1));// 9
// show(pairToString(list2));// (5, (4, (6, (1, (8, null)))))
// show(last(list2));// 8
// show(last(null));// 报错"链表是空的"

function member(x, ls) 
{
    if (ls == null)
    {
        return false;
    }
    else if (x == first(ls))
    {
        return true;
    }
    else
    {
        return member(x, second(ls));
    }
}
// show(pairToString(list2));// (5, (4, (6, (1, (8, null)))))
// show(member(3, list2));    // false
// show(member(4, list2));    // true
// show(member(0, null));

function rember(x, ls)
{
    if (ls == null)
    {
        return null;
    }
    else
    {
        if (x == head(ls))
        {
            return rember(x, tail(ls));
        }
        else
        {
            return pair(head(ls), rember(x, tail(ls)));
        }
    }
}
var listRember = pair(3, pair(7, pair(2, (pair(3, pair(4, pair(3, null)))))));
// show(pairToString(listRember));// (3, (7, (2, (3, (4, (3, null))))))
// show(pairToString(rember(2, listRember)));// (3, (7, (3, (4, (3, null)))))
// show(pairToString(rember(4, listRember)));// (3, (7, (2, (3, (3, null)))))
// show(pairToString(rember(3, listRember)));// (7, (2, (4, null)))


function take(ls, n)
{
  // 得到 ls 的前 n 个元素，把它们放在一个 list 里返回
  if (n == 0)
  {
      return null;
  }
  else 
  {
      if (ls == null)
      {
        throw "out of bound";
      }
      else
      {
          return pair(head(ls), take(tail(ls), n - 1));
      }
  }
}
var list2 = pair(5, pair(4, pair(6, pair(1, pair(8, null)))));
// show(pairToString(list2));// (5, (4, (6, (1, (8, null)))))
// show(pairToString(take(list2, 0)));// null
// show(pairToString(take(list2, 1)));// (5, null)
// show(pairToString(take(list2, 2)));// (5, (4, null))
// show(pairToString(take(list2, 3)));// (5, (4, (6, null)))
// show(pairToString(take(list2, 4)));// (5, (4, (6, (1, null))))
// show(pairToString(take(list2, 5)));// (5, (4, (6, (1, (8, null)))))
// show(pairToString(take(list2, 9)));// 报错：超出链表长度


function drop(ls, n)
{
  // 返回一个新的链表，它"去掉"了 ls 的前 n 个元素
}
var list2 = pair(5, pair(4, pair(6, pair(1, pair(8, null)))));
// show(pairToString(list2));// (5, (4, (6, (1, (8, null)))))
show(pairToString(drop(list2, 0)));// (5, (4, (6, (1, (8, null)))))
show(pairToString(drop(list2, 2)));// (6, (1, (8, null)))
show(pairToString(drop(list2, 3)));// (1, (8, null))
show(pairToString(drop(list2, 5)));// null
show(pairToString(drop(list2, 9)));// 报错：超出链表长度












