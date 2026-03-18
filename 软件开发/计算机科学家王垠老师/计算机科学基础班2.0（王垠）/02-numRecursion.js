var show = (x) => console.log(x);

function abs(x)
{
    if (x < 0)
    {
        return -x;
    }
    else
    {
        return x;
    }
}
// show(abs(-5));
// show(abs(5));

function sign(x)
{
    if (x < 0)
    {
        return -1;
    }
    else if (x > 0)
    {
        return 1;
    }
    else
    {
        return 0;
    }
}
// show(sign(-5));
// show(sign(0));
// show(sign(5));

function sum(n)
{
    if (n == 0)
    {
        return 0;
    }
    else
    {
        return n + sum(n - 1);
    }
}
// show(sum(5));    // 15

//数学表达阶乘: 
//5! = 5 * 4 * 3 * 2 * 1
//4! = 4 * 3 * 2 * 1
//5! = 5 * 4!
//4! = 4 * 3!
//......
//n! = n * (n - 1)! //所有自然数的阶乘
function fact(n)
{
    if (n > 0)
    {
        return n * fact(n - 1);
    }
    else //n <= 0
    {
        return 1;
    }
}
// show(fact(0));//1
// show(fact(1));//1
// show(fact(2));//2
// show(fact(3));//6
// show(fact(4));//24
// show(fact(5));//120

//unit 是 base case 返回的值（0 或者 1)
//combine 是递归情况返回时进行的“组合操作”（比如 + 或者 *）。
function accum(n, unit, combine)
{
    if (n == 0)
    {
        return unit;
    }
    else
    {
        return combine(n, accum(n - 1, unit, combine));
    }
}
function sum2(n)
{
    return accum(n, 0, (x, y) => x + y);
}
function fact2(n)
{
    return accum(n, 1, (x, y) => x * y); 
}
// show(sum2(0));//0
// show(sum2(5));//15
// show(fact2(0));//1
// show(fact2(5));//120

function sumFrom(a, b)
{
    if (a == b)
    {
        return a;
    }
    else
    {
        return a + sumFrom(a + 1, b);
    }
}
// show(sumFrom(3, 3));    // 3
// show(sumFrom(3, 5));    // 12

//输入自然数 b (base) 和 e (exponent)，它计算 b 的 e 次方的值。
function expt(b, e)
{
    if (e == 0)
    {
        return 1;
    }
    else
    {
        return b * expt(b, e - 1);
    }
}
// show(expt(2, 0));    // 1
// show(expt(3, 4));    // 81

function nest(f, n)
{
    if (n == 0)
    {
        return x => x;
    }
    else if (n == 1)
    {
        return x => f(x);
    }
    else
    {
        return x => f(nest(f, n - 1)(x));
    }
}
// show(nest(x => x + 1, 0)(3));  // 3
// show(nest(x => x + 1, 7)(0));  // 7
// show(nest(x => x * x, 3)(2));  // 256
// show(nest(x => 1 + 1/x, 100)(3));    // 这个结果看起来像什么数？
// show(nest(x => 1 + 1/x, 100)(42));
// show(nest(x => 1 + 1/x, 100)(-42));


function strange(n)
{
  if (n % 2 == 0)    // 如果 n 是偶数
  {
    return n / 2;
  }
  else
  {
    return 3 * n + 1;
  }
}
function checkStrange(start, depth)
{
  // 参数 start 是初始值，depth 用来限制最大深度。
  // 如果在最大深度还没有到 1，就返回 false。
}
show(checkStrange(6243, 10000));  // true
show(checkStrange(237, 10)); // false
show(checkStrange(237, 10000));   // true

