#include<bits/stdc++.h>
using namespace std;

struct Graph
{
    vector<vector<int>> data;
    int n;

    Graph(int n)
    {
        for (int i = 0; i < n; i++)
        {
            vector<int> v;
            for (int j = 0; j < n; j++)
            {
                v.push_back(0);
            }
            data.push_back(v);
        }
        this->n = n;
    }

    void set_data()
    {
        for (int i = 0; i < n; i++)
        {
            for (int j = 0; j < n; j++)
            {
                if (i != j)
                {
                    int val;
                    cout << "Enter 0 if no edge between " << i << " and " << j << " else enter 1" << endl;
                    cin >> val;
                    data[i][j] = val;
                }
            }
        }
    }

    void get_data()
    {
        for (int i = 0; i < n; i++)
        {
            for (int j = 0; j < n; j++)
            {
                cout << data[i][j] << " ";
            }
            cout << endl;
        }
    }

    void dfs(int source, vector<bool> &visited)
    {
        visited[source] = true;
        cout << source << " ";
        for (int i = 0; i < n; i++)
        {
            if (visited[i] == false)
            {
                if (data[source][i] != 0)
                {
                    dfs(i, visited);
                }
            }
        }
    }

    void bfs(int source, vector<bool> &visited)
    {
        queue<int> q;
        q.push(source);
        while (q.empty() != true)
        {
            int x = q.front();
            q.pop();
            visited[x] = true;
            cout << x << " ";
            for (int i = 0; i < n; i++)
            {
                if (visited[i] == false)
                {
                    if (data[x][i] != 0)
                    {
                        visited[i] = true;
                        q.push(i);
                    }
                }
            }
        }
    } 
};

int main()
{
    int n = 5;
    Graph graph = Graph(n);
    graph.set_data();
    graph.get_data();
    cout << endl;
    vector<bool> visited1(n, false);
    graph.dfs(0, visited1);
    cout << endl;
    cout << endl;
    vector<bool> visited2(n, false);
    graph.bfs(0, visited2);
    return 0;
}